import os
import json
import httpx
from fastapi import FastAPI, Request, Response, Header
from fastapi.responses import JSONResponse
import redis.asyncio as redis

app = FastAPI()

# Configurações (Lendo do ambiente Docker)
DJANGO_URL = os.getenv("DJANGO_BACKEND_URL", "http://backend:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis_cache:6379/1") # Usando DB 1 para separar do DB 0 do Django
CACHE_TTL = 15  # Cache curto de 15 segundos é suficiente para aliviar picos massivos

# Cliente Redis
redis_client = redis.from_url(REDIS_URL)

# Cliente HTTP Assíncrono (Reutiliza conexões)
http_client = httpx.AsyncClient(base_url=DJANGO_URL, timeout=180.0)

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()
    await redis_client.close()

async def get_cached_response(key: str):
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None

async def set_cached_response(key: str, data: dict, ttl: int):
    await redis_client.setex(key, ttl, json.dumps(data))

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_proxy(path: str, request: Request):
    """
    Proxy inteligente que faz cache de GETs e repassa o resto.
    """
    method = request.method
    # Constrói a URL completa para o Django
    query_params = str(request.query_params)
    url_path = f"/{path}" + (f"?{query_params}" if query_params else "")
    
    # Headers para repassar (Importante: Authorization e Content-Type)
    headers = dict(request.headers)
    headers.pop("host", None) # Deixa o httpx definir o host
    headers.pop("content-length", None) 

    # --- ESTRATÉGIA DE CACHE (Apenas para GET) ---
    if method == "GET":
        # A chave de cache DEVE incluir o Token de Autorização para garantir 
        # que um usuário não veja dados de outro.
        auth_token = headers.get("authorization", "public")
        cache_key = f"cache:{auth_token}:{url_path}"
        
        # 1. Tenta pegar do Redis
        cached_data = await get_cached_response(cache_key)
        if cached_data:
            # Retorna do cache com um header extra para debug
            return JSONResponse(content=cached_data, headers={"X-Cache": "HIT"})

    # 2. Se não for GET ou não estiver em cache, chama o Django
    try:
        content = await request.body()
        
        django_response = await http_client.request(
            method=method,
            url=url_path,
            headers=headers,
            content=content
        )
        
        response_content = django_response.content
        
        # Tenta converter para JSON se possível
        try:
            json_content = django_response.json()
            
            # 3. Se foi um GET bem sucedido (200 OK), salva no Redis
            if method == "GET" and django_response.status_code == 200:
                await set_cached_response(cache_key, json_content, CACHE_TTL)
                
            return JSONResponse(
                content=json_content, 
                status_code=django_response.status_code,
                headers={"X-Cache": "MISS"}
            )
            
        except json.JSONDecodeError:
            # Se não for JSON (ex: arquivo, imagem), retorna os bytes crus
            return Response(
                content=response_content,
                status_code=django_response.status_code,
                media_type=django_response.headers.get("content-type")
            )

    except httpx.RequestError as exc:
        return JSONResponse(
            content={"detail": f"Erro de comunicação com o backend: {str(exc)}"},
            status_code=502
        )