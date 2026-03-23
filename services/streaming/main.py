import asyncio
import logging
import time
import subprocess
import tempfile
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any

import httpx
from fastapi import FastAPI, WebSocket, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import redis.asyncio as aioredis

# ============================================
# CONFIGURAÇÃO
# ============================================

class Settings(BaseSettings):
    # MediaMTX
    mediamtx_api_url: str = "http://mediamtx:9997"
    mediamtx_hls_url: str = "http://mediamtx:8888"
    mediamtx_webrtc_url: str = "http://mediamtx:8889"
    mediamtx_api_user: str = "mediamtx_api_user"
    mediamtx_api_pass: str = "GtV!sionMed1aMTX$2025"
    
    # Redis
    redis_url: str = "redis://redis_cache:6379/2"
    
    # Performance
    max_connections_per_stream: int = 100
    health_check_interval: int = 15
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("streaming")

# ============================================
# MODELOS
# ============================================

class StreamInfo(BaseModel):
    path: str
    source: Optional[Dict[str, Any]] = None
    ready: bool = False
    readers: int = 0
    bytes_received: int = 0
    bytes_sent: int = 0

class StreamStats(BaseModel):
    active_streams: int = 0
    total_viewers: int = 0
    uptime_seconds: float = 0
    streams: List[StreamInfo] = Field(default_factory=list)

class ProvisionRequest(BaseModel):
    camera_id: int
    rtsp_url: str
    name: str
    # CORREÇÃO CRÍTICA 1: Adicionado campo 'enabled' para compatibilidade com Django
    enabled: bool = True 
    on_demand: bool = True

class ProvisionResponse(BaseModel):
    success: bool
    camera_id: int
    stream_path: str
    hls_url: str
    message: str = ""

# ============================================
# GERENCIADOR DE CONEXÕES
# ============================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, stream_path: str) -> bool:
        async with self._lock:
            if stream_path not in self.active_connections:
                self.active_connections[stream_path] = set()
            if len(self.active_connections[stream_path]) >= settings.max_connections_per_stream:
                return False
            await websocket.accept()
            self.active_connections[stream_path].add(websocket)
            return True
    
    async def disconnect(self, websocket: WebSocket, stream_path: str):
        async with self._lock:
            if stream_path in self.active_connections:
                self.active_connections[stream_path].discard(websocket)
                if not self.active_connections[stream_path]:
                    del self.active_connections[stream_path]
    
    def get_total_viewers(self) -> int:
        return sum(len(conns) for conns in self.active_connections.values())

# ============================================
# SERVIÇO PRINCIPAL
# ============================================

class StreamingService:
    def __init__(self):
        self.auth = (settings.mediamtx_api_user, settings.mediamtx_api_pass)
        self.connections = ConnectionManager()
        self.redis: Optional[aioredis.Redis] = None
        self.start_time = time.time()
        self._client = httpx.AsyncClient(timeout=10.0)

    async def initialize(self):
        try:
            self.redis = await aioredis.from_url(settings.redis_url)
            await self.redis.ping()
            logger.info("Conectado ao Redis")
            await self._restore_cameras_from_redis()
        except Exception as e:
            logger.warning(f"Redis indisponível: {e}")
        asyncio.create_task(self._periodic_health_check())

    async def _restore_cameras_from_redis(self):
        """Restaura câmeras do Redis após restart."""
        if not self.redis:
            return
        try:
            keys = await self.redis.keys("camera:*")
            restored = 0
            for key in keys:
                data = await self.redis.hgetall(key)
                if data:
                    camera_id = int(data[b'camera_id'])
                    rtsp_url = data[b'rtsp_url'].decode()
                    name = data[b'name'].decode()
                    enabled = data.get(b'enabled', b'true') == b'true'
                    
                    if enabled:
                        req = ProvisionRequest(
                            camera_id=camera_id,
                            rtsp_url=rtsp_url,
                            name=name,
                            enabled=True,
                            on_demand=True
                        )
                        result = await self.provision_camera(req)
                        if result.success:
                            restored += 1
            if restored > 0:
                logger.info(f"✅ {restored} câmeras restauradas do Redis")
        except Exception as e:
            logger.error(f"Erro ao restaurar câmeras: {e}")

    async def _periodic_health_check(self):
        while True:
            try:
                await asyncio.sleep(settings.health_check_interval)
                if self.redis:
                    stats = await self.get_stats()
                    await self.redis.set("streaming:stats", stats.model_dump_json(), ex=60)
            except Exception as e:
                logger.error(f"Erro no loop de stats: {e}")

    async def _validate_rtsp_stream(self, rtsp_url: str) -> bool:
        """Valida stream RTSP antes de provisionar."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "ffprobe", "-v", "error", "-rtsp_transport", "tcp",
                "-i", rtsp_url, "-show_entries", "stream=codec_type",
                "-of", "default=noprint_wrappers=1",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            return b"video" in stdout
        except:
            return False

    async def provision_camera(self, request: ProvisionRequest) -> ProvisionResponse:
        stream_path = f"cam_{request.camera_id}"

        # RTMP push: camera envia stream para nós (sem source URL)
        is_rtmp_push = not request.rtsp_url or request.rtsp_url.startswith('rtmp_push://')

        if is_rtmp_push:
            config = {
                "source": "publisher",
                "sourceOnDemand": False,
                "overridePublisher": True,
            }
        else:
            config = {
                "source": request.rtsp_url,
                "sourceOnDemand": request.on_demand,
                "rtspTransport": "tcp"
            }
        
        logger.info(f"Provisionando {stream_path}")
        
        try:
            # Tenta criar (POST)
            resp = await self._client.post(
                f"{settings.mediamtx_api_url}/v3/config/paths/add/{stream_path}", 
                json=config,
                auth=self.auth
            )
            
            # Se conflito (409 - já existe), atualiza (PATCH)
            if resp.status_code == 409:
                resp = await self._client.patch(
                    f"{settings.mediamtx_api_url}/v3/config/paths/patch/{stream_path}", 
                    json=config,
                    auth=self.auth
                )
            
            if resp.status_code in [200, 201, 204]:
                # Persiste no Redis para fallback
                if self.redis:
                    await self.redis.hset(
                        f"camera:{request.camera_id}",
                        mapping={
                            "camera_id": request.camera_id,
                            "rtsp_url": request.rtsp_url,
                            "name": request.name,
                            "enabled": str(request.enabled).lower(),
                            "stream_path": stream_path
                        }
                    )
                
                # Notifica LPR via RabbitMQ (apenas RTSP)
                if request.rtsp_url.startswith('rtsp://'):
                    try:
                        import aio_pika
                        import json
                        
                        connection = await aio_pika.connect_robust(
                            "amqp://gtvision_user:your-rabbitmq-password-here@rabbitmq:5672/"
                        )
                        async with connection:
                            channel = await connection.channel()
                            await channel.default_exchange.publish(
                                aio_pika.Message(body=json.dumps({
                                    "camera_id": request.camera_id,
                                    "stream_path": stream_path
                                }).encode()),
                                routing_key="lpr_queue"
                            )
                        logger.info(f"🤖 LPR notificado via RabbitMQ para câmera {request.camera_id}")
                    except Exception as e:
                        logger.error(f"Erro ao publicar no RabbitMQ: {e}")
                
                return ProvisionResponse(
                    success=True, 
                    camera_id=request.camera_id, 
                    stream_path=stream_path,
                    hls_url=f"/hls/{stream_path}/index.m3u8",
                    message="Provisionamento OK"
                )
            else:
                raise Exception(f"MediaMTX Error {resp.status_code}: {resp.text}")
                
        except Exception as e:
            logger.error(f"Erro ao provisionar {stream_path}: {str(e)}")
            return ProvisionResponse(
                success=False, 
                camera_id=request.camera_id, 
                stream_path="", 
                hls_url="", 
                message=str(e)
            )

    async def list_streams(self) -> List[StreamInfo]:
        try:
            resp = await self._client.get(
                f"{settings.mediamtx_api_url}/v3/paths/list", 
                auth=self.auth
            )
            items = resp.json().get("items", [])
            return [
                StreamInfo(
                    path=item.get("name", ""),
                    ready=item.get("ready", False),
                    readers=len(item.get("readers", [])),
                    bytes_received=item.get("bytesReceived", 0),
                    bytes_sent=item.get("bytesSent", 0)
                ) for item in items if item.get("name", "").startswith("cam_")
            ]
        except Exception as e:
            logger.error(f"Erro ao listar: {e}")
            return []

    async def get_stats(self) -> StreamStats:
        streams = await self.list_streams()
        return StreamStats(
            active_streams=sum(1 for s in streams if s.ready),
            total_viewers=self.connections.get_total_viewers(),
            streams=streams,
            uptime_seconds=time.time() - self.start_time
        )
    
    async def get_camera_status(self, camera_id: int) -> dict:
        stream_path = f"cam_{camera_id}"
        try:
            resp = await self._client.get(
                f"{settings.mediamtx_api_url}/v3/paths/get/{stream_path}",
                auth=self.auth
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "status": "ready" if data.get("ready") else "waiting",
                    "viewers": len(data.get("readers", [])),
                    "source": data.get("source"),
                    "hls_url": f"/hls/{stream_path}/index.m3u8"
                }
            return {"status": "not_found"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

streaming_service = StreamingService()

# ============================================
# APP
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    await streaming_service.initialize()
    yield
    await streaming_service._client.aclose()

app = FastAPI(title="GT-Vision Streaming Service", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow()}

@app.post("/cameras/provision", response_model=ProvisionResponse)
async def provision(request: ProvisionRequest):
    return await streaming_service.provision_camera(request)

@app.delete("/cameras/{camera_id}")
async def remove_camera(camera_id: int):
    stream_path = f"cam_{camera_id}"
    try:
        await streaming_service._client.delete(
            f"{settings.mediamtx_api_url}/v3/config/paths/delete/{stream_path}",
            auth=streaming_service.auth
        )
        # Remove do Redis
        if streaming_service.redis:
            await streaming_service.redis.delete(f"camera:{camera_id}")
        return {"success": True}
    except:
        return {"success": False}

@app.get("/cameras/{camera_id}/status")
async def camera_status(camera_id: int):
    return await streaming_service.get_camera_status(camera_id)

@app.get("/stats", response_model=StreamStats)
async def get_stats():
    return await streaming_service.get_stats()

@app.get("/cameras/{camera_id}/snapshot")
async def get_snapshot(camera_id: int):
    """Retorna snapshot em cache ou captura novo se não existir."""
    cache_key = f"snapshot:cam_{camera_id}"
    
    # Verifica cache no Redis
    if streaming_service.redis:
        try:
            cached = await streaming_service.redis.get(cache_key)
            if cached:
                return Response(content=cached, media_type="image/jpeg")
        except Exception as e:
            logger.warning(f"Erro ao ler cache: {e}")
    
    # Captura novo snapshot
    stream_path = f"cam_{camera_id}"
    rtsp_url = f"rtsp://mediamtx:8554/{stream_path}"
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp_path = tmp.name
        
        # FFmpeg captura 1 frame
        cmd = [
            "ffmpeg", "-y",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-frames:v", "1",
            "-q:v", "2",
            tmp_path
        ]
        
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await asyncio.wait_for(proc.communicate(), timeout=10)
        
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
            with open(tmp_path, "rb") as f:
                img_data = f.read()
            
            os.unlink(tmp_path)
            
            # Salva no cache (24h)
            if streaming_service.redis:
                try:
                    await streaming_service.redis.set(cache_key, img_data, ex=86400)
                except Exception as e:
                    logger.warning(f"Erro ao salvar cache: {e}")
            
            return Response(content=img_data, media_type="image/jpeg")
        
        raise Exception("Snapshot vazio")
        
    except Exception as e:
        logger.error(f"Erro ao capturar snapshot cam_{camera_id}: {e}")
        raise HTTPException(status_code=503, detail="Câmera offline")

@app.get("/hls/{stream_path}/{file_name}")
async def proxy_hls(stream_path: str, file_name: str):
    """Proxy HLS com auto-provision se câmera não existir."""
    url = f"{settings.mediamtx_hls_url}/{stream_path}/{file_name}"
    try:
        resp = await streaming_service._client.get(url, timeout=5.0)
        if resp.status_code == 200:
            media_type = "application/vnd.apple.mpegurl" if file_name.endswith(".m3u8") else "video/MP2T"
            return Response(content=resp.content, media_type=media_type)
        
        # 404: Câmera não provisionada, tentar auto-provision
        if resp.status_code == 404 and file_name == "index.m3u8" and stream_path.startswith("cam_"):
            camera_id = int(stream_path.replace("cam_", ""))
            logger.warning(f"Stream {stream_path} não encontrado, tentando auto-provision...")
            
            # Buscar câmera do Redis
            if streaming_service.redis:
                camera_data = await streaming_service.redis.hgetall(f"camera:{camera_id}")
                if camera_data:
                    req = ProvisionRequest(
                        camera_id=camera_id,
                        rtsp_url=camera_data[b'rtsp_url'].decode(),
                        name=camera_data[b'name'].decode(),
                        enabled=True,
                        on_demand=True
                    )
                    result = await streaming_service.provision_camera(req)
                    if result.success:
                        # Aguardar stream ficar pronto
                        await asyncio.sleep(2)
                        resp = await streaming_service._client.get(url, timeout=5.0)
                        if resp.status_code == 200:
                            media_type = "application/vnd.apple.mpegurl"
                            return Response(content=resp.content, media_type=media_type)
        
        raise HTTPException(status_code=404, detail="Stream not found")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="MediaMTX timeout")
    except Exception as e:
        logger.error(f"Erro no proxy HLS: {e}")
        raise HTTPException(status_code=502, detail="MediaMTX indisponível")