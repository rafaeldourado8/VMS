from fastapi import APIRouter, Depends
from datetime import datetime
import psutil
import logging

from ..services.stream_manager import StreamManager
from ..services.cache_service import RedisCacheService
from ..core.dependencies import get_stream_service, get_cache_service
from ..schemas import HealthResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", response_model=HealthResponse)
async def health_check(
    stream_service: StreamManager = Depends(get_stream_service),
    cache_service: RedisCacheService = Depends(get_cache_service)
):
    """Health check endpoint"""
    
    # Verifica Redis
    redis_status = "healthy"
    try:
        await cache_service.set("health_check", "ok", ttl=10)
        result = await cache_service.get("health_check")
        if result != "ok":
            redis_status = "unhealthy"
    except:
        redis_status = "unhealthy"
    
    # Informações do sistema
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    # Informações dos streams
    streams = stream_service.list_streams()
    active_streams = len([s for s in streams if s.is_active])
    
    return HealthResponse(
        status="healthy" if redis_status == "healthy" else "degraded",
        timestamp=datetime.now(),
        version="1.0.0",
        services={
            "redis": redis_status,
            "streaming": "healthy"
        },
        metrics={
            "active_streams": active_streams,
            "total_streams": len(streams),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024)
        }
    )

@router.get("/ready")
async def readiness_check():
    """Readiness check para Kubernetes"""
    return {"status": "ready"}

@router.get("/live")
async def liveness_check():
    """Liveness check para Kubernetes"""
    return {"status": "alive"}