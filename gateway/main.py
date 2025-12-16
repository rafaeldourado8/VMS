import os
import json
import httpx
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from pydantic import BaseModel
from datetime import datetime

# Importações Locais
from database import connect_dbs, disconnect_dbs, get_reader_db, database_writer, detections_table
from services.stream import StreamService

# --- CONFIGURAÇÕES ---
DJANGO_URL = os.getenv("DJANGO_BACKEND_URL", "http://backend:8000")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis_cache:6379/1")
CACHE_TTL = 5

# Modelo para Ingestão de Dados da IA (LPR)
class LPRDetection(BaseModel):
    camera_id: int
    plate: str
    confidence: float
    timestamp: datetime
    image_url: str | None = None
    metadata: dict | None = {}

# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Conectar DBs e Redis
    await connect_dbs()
    app.state.redis = redis.from_url(REDIS_URL)
    app.state.http_client = httpx.AsyncClient(base_url=DJANGO_URL, timeout=60.0)
    app.state.stream_service = StreamService(app.state.redis)
    
    # Iniciar Monitoramento em Background
    task = asyncio.create_task(background_status_checker(app))
    
    yield
    
    # Desligar
    task.cancel()
    await app.state.http_client.aclose()
    await app.state.redis.close()
    await disconnect_dbs()

async def background_status_checker(app):
    """Loop infinito que verifica status das câmeras"""
    while True:
        try:
            # Usa conexão de LEITURA (Replica) para não pesar o Master
            reader = await get_reader_db()
            await app.state.stream_service.update_cameras_status(reader)
        except Exception as e:
            print(f"Erro no monitoramento: {e}")
        await asyncio.sleep(5)

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENDPOINTS DE ALTA PERFORMANCE (FastAPI Puro) ---

@app.post("/fast-api/ingest/lpr")
async def ingest_lpr_detection(detection: LPRDetection):
    """
    Recebe detecção de placa (IA).
    Escreve direto no DB Master via SQLAlchemy Core (Async).
    """
    # CORREÇÃO: Usando nomes de colunas em Inglês para bater com o Django
    query = detections_table.insert().values(
        camera_id=detection.camera_id,
        plate=detection.plate,           # Alterado de 'placa'
        confidence=detection.confidence, # Alterado de 'confianca'
        timestamp=detection.timestamp,   # Alterado de 'horario'
        image_url=detection.image_url    # Alterado de 'imagem_url'
    )
    
    try:
        record_id = await database_writer.execute(query)
        return {"status": "received", "id": record_id}
    except Exception as e:
        print(f"Erro ao salvar detecção: {e}")
        raise HTTPException(status_code=500, detail="Failed to save detection")

@app.get("/fast-api/cameras/status")
async def get_all_cameras_status():
    """
    Retorna status de todas as câmeras lendo do Redis.
    Zero load no DB.
    """
    keys = await app.state.redis.keys("camera:*:status")
    if not keys:
        return []
    
    values = await app.state.redis.mget(keys)
    results = []
    for key, val in zip(keys, values):
        # key format: camera:{id}:status
        cam_id = key.decode().split(":")[1]
        status = val.decode() if val else "offline"
        results.append({"id": int(cam_id), "status": status})
        
    return results

@app.get("/fast-api/camera/{camera_id}/playback")
async def get_camera_playback(camera_id: int, start: str, end: str):
    manifest = await app.state.stream_service.get_playback_manifest(camera_id, start, end)
    return Response(content=manifest, media_type="application/vnd.apple.mpegurl")

# --- PROXY INTELIGENTE (Para o Django) ---

async def get_cached_response(redis_conn, key: str):
    data = await redis_conn.get(key)
    return json.loads(data) if data else None

async def set_cached_response(redis_conn, key: str, data: dict, ttl: int):
    await redis_conn.setex(key, ttl, json.dumps(data))

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def gateway_proxy(path: str, request: Request):
    # Se for rota interna do FastAPI, deixa passar
    if path.startswith("fast-api") or path.startswith("docs") or path.startswith("openapi"):
        return await request.app.router.handle(request)

    method = request.method
    query_params = str(request.query_params)
    url_path = f"/{path}" + (f"?{query_params}" if query_params else "")
    
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)

    # ✅ NUNCA cachear rotas de autenticação
    is_auth_route = path.startswith("api/auth/")
    should_cache = method == "GET" and not is_auth_route
    
    if should_cache:
        auth_token = headers.get("authorization", "public")
        cache_key = f"cache:{auth_token}:{url_path}"
        
        cached = await get_cached_response(app.state.redis, cache_key)
        if cached:
            return JSONResponse(content=cached, headers={"X-Cache": "HIT"})

    try:
        content = await request.body()
        
        django_resp = await app.state.http_client.request(
            method=method,
            url=url_path,
            headers=headers,
            content=content
        )
        
        # Tenta salvar no cache se foi sucesso
        if should_cache and django_resp.status_code == 200:
            try:
                json_data = django_resp.json()
                await set_cached_response(app.state.redis, cache_key, json_data, CACHE_TTL)
                return JSONResponse(content=json_data, headers={"X-Cache": "MISS"})
            except:
                pass # Não é JSON, retorna raw

        return Response(
            content=django_resp.content,
            status_code=django_resp.status_code,
            media_type=django_resp.headers.get("content-type"),
            headers={"X-Cache": "MISS"}
        )

    except httpx.RequestError as exc:
        return JSONResponse(
            content={"detail": "Backend unavailable"},
            status_code=502
        )