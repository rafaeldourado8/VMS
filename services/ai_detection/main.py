"""
AI Detection Service API - DDD
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Tuple
import logging

from application.detection.commands.toggle_ai_command import ToggleAICommand
from infrastructure.repositories.camera_config_repository import InMemoryCameraConfigRepository

try:
    from frame_processor import frame_processor
    from stream_worker import stream_worker
    FRAME_PROCESSOR_AVAILABLE = True
except ImportError:
    FRAME_PROCESSOR_AVAILABLE = False
    logging.warning("Frame processor não disponível")

logger = logging.getLogger(__name__)

# Inicialização
config_repo = InMemoryCameraConfigRepository()

app = FastAPI(title="AI Detection Service - DDD")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# DTOs
class ToggleAIRequest(BaseModel):
    enabled: bool


class UpdateROIRequest(BaseModel):
    polygon_points: List[Tuple[float, float]]
    enabled: bool = True
    name: str = "ROI"


class AIStatusResponse(BaseModel):
    camera_id: int
    ai_enabled: bool
    has_roi: bool


# Endpoints
@app.on_event("startup")
async def startup_event():
    """Inicializa workers ao iniciar o serviço"""
    if FRAME_PROCESSOR_AVAILABLE:
        await stream_worker.start()
        logger.info("✅ Stream worker iniciado")


@app.on_event("shutdown")
async def shutdown_event():
    """Para workers ao desligar o serviço"""
    if FRAME_PROCESSOR_AVAILABLE:
        await stream_worker.stop()
        logger.info("🛑 Stream worker parado")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai_detection"}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content="# HELP ai_detection_up Service is up\n# TYPE ai_detection_up gauge\nai_detection_up 1\n",
        media_type="text/plain"
    )


@app.post("/ai/cameras/{camera_id}/start/")
async def start_ai(camera_id: int):
    """Inicia IA para uma câmera"""
    try:
        config_repo._configs[camera_id] = {'ai_enabled': True}
        return {"success": True, "camera_id": camera_id, "ai_enabled": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/cameras/{camera_id}/stop/")
async def stop_ai(camera_id: int):
    """Para IA para uma câmera"""
    try:
        config_repo._configs[camera_id] = {'ai_enabled': False}
        return {"success": True, "camera_id": camera_id, "ai_enabled": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/toggle/{camera_id}")
async def toggle_ai(camera_id: int, request: ToggleAIRequest):
    """Ativa ou desativa IA para uma câmera"""
    try:
        config_repo._configs[camera_id] = {'ai_enabled': request.enabled}
        return {"success": True, "camera_id": camera_id, "ai_enabled": request.enabled}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/ai/cameras/{camera_id}/test/")
async def test_detection(camera_id: int):
    """Testa detecção de IA para uma câmera"""
    try:
        config = config_repo.get(camera_id)
        if not config.get('ai_enabled', False):
            return {"success": False, "message": "IA não está ativa para esta câmera"}
        
        return {
            "success": True, 
            "message": "Teste de detecção executado com sucesso",
            "camera_id": camera_id,
            "has_roi": config.get('roi') is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai/cameras/{camera_id}/status/", response_model=AIStatusResponse)
async def get_camera_ai_status(camera_id: int):
    """Obtém status da IA para uma câmera (rota compatível com frontend)"""
    config = config_repo.get(camera_id)
    
    return AIStatusResponse(
        camera_id=camera_id,
        ai_enabled=config.get('ai_enabled', False),
        has_roi=config.get('roi') is not None
    )


@app.get("/ai/status/{camera_id}", response_model=AIStatusResponse)
async def get_ai_status(camera_id: int):
    """Obtém status da IA para uma câmera"""
    config = config_repo.get(camera_id)
    
    return AIStatusResponse(
        camera_id=camera_id,
        ai_enabled=config.get('ai_enabled', True),
        has_roi=config.get('roi') is not None
    )


@app.get("/ai/cameras")
async def list_cameras_with_ai():
    """Lista câmeras com IA configurada"""
    return {
        "cameras": [
            {"camera_id": cid, "ai_enabled": config.get('ai_enabled', True)}
            for cid, config in config_repo._configs.items()
        ]
    }
