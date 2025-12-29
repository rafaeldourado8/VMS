"""
GT-Vision Streaming Service - VERSÃO CORRIGIDA
=====================================================
Serviço de alta performance para streaming de vídeo via HLS e WebSocket.
CORREÇÃO: recordPath deve conter %path literal (não interpolado)
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Path, Response
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
    mediamtx_rtsp_url: str = "rtsp://mediamtx:8554"
    mediamtx_api_user: str = "mediamtx_api_user"
    mediamtx_api_pass: str = "GtV!sionMed1aMTX$2025"
    
    # Redis
    redis_url: str = "redis://redis_cache:6379/2"
    
    # Performance
    max_connections_per_stream: int = 100
    health_check_interval: int = 15
    hls_segment_cache_ttl: int = 5
    
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
    """Informações de um stream mapeadas da API v3."""
    path: str
    source: Optional[Dict[str, Any]] = None
    ready: bool = False
    readers: int = 0
    bytes_received: int = 0
    bytes_sent: int = 0

class CameraStream(BaseModel):
    """Representação de uma câmera para o frontend."""
    camera_id: int
    name: str
    stream_path: str
    rtsp_url: str
    hls_url: Optional[str] = None
    webrtc_url: Optional[str] = None
    status: str = "unknown"
    last_check: Optional[datetime] = None

class StreamStats(BaseModel):
    """Estatísticas globais."""
    active_streams: int = 0
    total_viewers: int = 0
    total_bytes_sent: int = 0
    uptime_seconds: float = 0
    streams: List[StreamInfo] = Field(default_factory=list)

class ProvisionRequest(BaseModel):
    camera_id: int
    rtsp_url: str
    name: str
    on_demand: bool = True

class ProvisionResponse(BaseModel):
    success: bool
    camera_id: int
    stream_path: str
    hls_url: str
    webrtc_url: str
    message: str = ""

# ============================================
# GERENCIADOR DE CONEXÕES
# ============================================

class ConnectionManager:
    """Gerencia WebSockets para o dashboard e eventos."""
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
        self._client = httpx.AsyncClient(timeout=10.0, auth=self.auth)
        self.drift_monitor = None

    async def initialize(self):
        try:
            self.redis = await aioredis.from_url(settings.redis_url)
            await self.redis.ping()
            logger.info("Conectado ao Redis")
        except Exception as e:
            logger.warning(f"Redis indisponível: {e}")
        
        # Inicia monitor de drift (opcional)
        try:
            from .drift_monitor import start_drift_monitor
            self.drift_monitor = await start_drift_monitor(
                settings.mediamtx_api_url, 
                self.auth
            )
            logger.info("🔍 Monitor de drift iniciado")
        except ImportError:
            logger.warning("Monitor de drift não disponível")
        
        asyncio.create_task(self._periodic_health_check())

    async def _periodic_health_check(self):
        while True:
            try:
                await asyncio.sleep(settings.health_check_interval)
                if self.redis:
                    stats = await self.get_stats()
                    await self.redis.set("streaming:stats", stats.model_dump_json(), ex=60)
            except Exception as e:
                logger.error(f"Erro no loop de stats: {e}")

    async def provision_camera(self, request: ProvisionRequest) -> ProvisionResponse:
        """Adiciona câmara ao MediaMTX com configurações otimizadas para estabilidade."""
        stream_path = f"cam_{request.camera_id}"
        
        # Configurações otimizadas para evitar drift
        record_path = "/recordings/%path/%Y-%m-%d_%H-%M-%S-%f"
        
        config = {
            "source": request.rtsp_url,
            "sourceOnDemand": request.on_demand,
            "sourceOnDemandStartTimeout": "30s",
            "sourceOnDemandCloseAfter": "60s",
            "rtspTransport": "tcp",
            "rtspUDPReadBufferSize": 33554432,
            "useAbsoluteTimestamp": False,  # CRÍTICO: evita drift
            "record": True,
            "recordPath": record_path,
            "recordFormat": "fmp4",
            "recordPartDuration": "4s",
            "recordSegmentDuration": "30m",
            "maxReaders": 10
        }
        
        logger.info(f"Provisionando {stream_path} com config: {config}")
        
        try:
            # Adiciona ou atualiza via API v3
            resp = await self._client.post(
                f"{settings.mediamtx_api_url}/v3/config/paths/add/{stream_path}", 
                json=config
            )
            
            if resp.status_code == 409:
                # Path já existe, atualiza
                logger.info(f"Path {stream_path} já existe, atualizando...")
                resp = await self._client.patch(
                    f"{settings.mediamtx_api_url}/v3/config/paths/patch/{stream_path}", 
                    json=config
                )
            
            if resp.status_code in [200, 201, 204]:
                logger.info(f"✅ Path {stream_path} provisionado com sucesso")
                return ProvisionResponse(
                    success=True, 
                    camera_id=request.camera_id, 
                    stream_path=stream_path,
                    hls_url=f"{settings.mediamtx_hls_url}/{stream_path}/index.m3u8",
                    webrtc_url=f"{settings.mediamtx_webrtc_url}/{stream_path}",
                    message="Provisionamento OK"
                )
            else:
                error_msg = f"HTTP {resp.status_code}: {resp.text}"
                logger.error(f"❌ Falha no provisionamento: {error_msg}")
                return ProvisionResponse(
                    success=False, 
                    camera_id=request.camera_id, 
                    stream_path="", 
                    hls_url="", 
                    webrtc_url="", 
                    message=error_msg
                )
                
        except Exception as e:
            logger.error(f"❌ Erro ao provisionar {stream_path}: {str(e)}")
            return ProvisionResponse(
                success=False, 
                camera_id=request.camera_id, 
                stream_path="", 
                hls_url="", 
                webrtc_url="", 
                message=str(e)
            )

    async def remove_camera(self, camera_id: int) -> bool:
        """Remove câmera do MediaMTX."""
        stream_path = f"cam_{camera_id}"
        try:
            resp = await self._client.delete(
                f"{settings.mediamtx_api_url}/v3/config/paths/delete/{stream_path}"
            )
            if resp.status_code in [200, 404]:
                logger.info(f"🗑️ Path {stream_path} removido")
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao remover {stream_path}: {e}")
            return False

    async def list_streams(self) -> List[StreamInfo]:
        """Mapeia os campos da API v3 para o modelo interno."""
        try:
            resp = await self._client.get(f"{settings.mediamtx_api_url}/v3/paths/list")
            items = resp.json().get("items", [])
            return [
                StreamInfo(
                    path=item.get("name", ""),
                    source=item.get("source"),
                    ready=item.get("ready", False),
                    readers=len(item.get("readers", [])),
                    bytes_received=item.get("bytesReceived", 0),
                    bytes_sent=item.get("bytesSent", 0)
                ) for item in items
            ]
        except Exception as e:
            logger.error(f"Erro ao listar: {e}")
            return []

    async def get_stats(self) -> StreamStats:
        streams = await self.list_streams()
        return StreamStats(
            active_streams=sum(1 for s in streams if s.ready),
            total_viewers=self.connections.get_total_viewers(),
            total_bytes_sent=sum(s.bytes_sent for s in streams),
            uptime_seconds=time.time() - self.start_time,
            streams=streams
        )

    async def get_camera_status(self, camera_id: int) -> dict:
        """Retorna status de uma câmera específica."""
        stream_path = f"cam_{camera_id}"
        try:
            resp = await self._client.get(
                f"{settings.mediamtx_api_url}/v3/paths/get/{stream_path}"
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
# FASTAPI APP
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

@app.get("/stats", response_model=StreamStats)
async def get_stats():
    return await streaming_service.get_stats()

@app.post("/cameras/provision", response_model=ProvisionResponse)
async def provision(request: ProvisionRequest):
    return await streaming_service.provision_camera(request)

@app.delete("/cameras/{camera_id}")
async def remove_camera(camera_id: int):
    success = await streaming_service.remove_camera(camera_id)
    return {"success": success}

@app.get("/cameras/{camera_id}/status")
async def camera_status(camera_id: int):
    return await streaming_service.get_camera_status(camera_id)

@app.get("/hls/{stream_path}/index.m3u8")
async def get_hls(stream_path: str):
    """Proxy para playlist HLS."""
    try:
        resp = await streaming_service._client.get(
            f"{settings.mediamtx_hls_url}/{stream_path}/index.m3u8"
        )
        if resp.status_code == 200:
            return Response(content=resp.content, media_type="application/vnd.apple.mpegurl")
    except Exception as e:
        logger.error(f"Erro ao obter HLS: {e}")
    raise HTTPException(status_code=404, detail="Stream não encontrado")

@app.get("/streams")
async def list_streams():
    """Lista todos os streams ativos."""
    return await streaming_service.list_streams()