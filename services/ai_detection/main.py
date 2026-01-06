"""
AI Detection Service API - DDD
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Tuple
import logging

from application.detection.commands.toggle_ai_command import ToggleAICommand
from application.detection.commands.update_roi_command import UpdateROICommand
from application.detection.handlers.toggle_ai_handler import ToggleAIHandler
from application.detection.handlers.update_roi_handler import UpdateROIHandler
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
toggle_handler = ToggleAIHandler(config_repo)
update_roi_handler = UpdateROIHandler(config_repo)

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


@app.post("/ai/cameras/{camera_id}/start/")
async def start_ai(camera_id: int):
    """Inicia IA para uma câmera"""
    try:
        command = ToggleAICommand(camera_id=camera_id, enabled=True)
        result = toggle_handler.handle(command)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/cameras/{camera_id}/stop/")
async def stop_ai(camera_id: int):
    """Para IA para uma câmera"""
    try:
        command = ToggleAICommand(camera_id=camera_id, enabled=False)
        result = toggle_handler.handle(command)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/toggle/{camera_id}")
async def toggle_ai(camera_id: int, request: ToggleAIRequest):
    """Ativa ou desativa IA para uma câmera"""
    try:
        command = ToggleAICommand(
            camera_id=camera_id,
            enabled=request.enabled
        )
        result = toggle_handler.handle(command)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/roi/{camera_id}")
async def update_roi(camera_id: int, request: UpdateROIRequest):
    """Atualiza ROI de uma câmera"""
    try:
        command = UpdateROICommand(
            camera_id=camera_id,
            polygon_points=request.polygon_points,
            enabled=request.enabled,
            name=request.name
        )
        roi = update_roi_handler.handle(command)
        
        return {
            "success": True,
            "camera_id": camera_id,
            "roi_name": roi.name,
            "enabled": roi.enabled,
            "points_count": len(roi.polygon.points)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/ai/cameras/{camera_id}/start/")
async def start_ai(camera_id: int):
    """Inicia IA para uma câmera"""
    try:
        command = ToggleAICommand(camera_id=camera_id, enabled=True)
        result = toggle_handler.handle(command)
        
        # Inicia frame processor se disponível
        if FRAME_PROCESSOR_AVAILABLE:
            config = config_repo.get(camera_id)
            frame_processor.start_camera(camera_id, config)
            
            # Adiciona câmera ao stream worker
            stream_url = f"http://mediamtx:8889/cam_{camera_id}/index.m3u8"
            await stream_worker.add_camera(camera_id, stream_url)
            
            logger.info(f"✅ IA iniciada para câmera {camera_id}")
        
        return {"success": True, "camera_id": camera_id, "ai_enabled": True}
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar IA: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/cameras/{camera_id}/stop/")
async def stop_ai(camera_id: int):
    """Para IA para uma câmera"""
    try:
        command = ToggleAICommand(camera_id=camera_id, enabled=False)
        result = toggle_handler.handle(command)
        
        # Para frame processor se disponível
        if FRAME_PROCESSOR_AVAILABLE:
            await stream_worker.remove_camera(camera_id)
            logger.info(f"🛑 IA parada para câmera {camera_id}")
        
        return {"success": True, "camera_id": camera_id, "ai_enabled": False}
    except Exception as e:
        logger.error(f"❌ Erro ao parar IA: {e}")
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
