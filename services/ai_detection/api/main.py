"""
AI Detection Service API - DDD
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Tuple

from application.detection.commands.toggle_ai_command import ToggleAICommand
from application.detection.handlers.toggle_ai_handler import ToggleAIHandler
from infrastructure.repositories.camera_config_repository import InMemoryCameraConfigRepository

# Inicialização
config_repo = InMemoryCameraConfigRepository()
toggle_handler = ToggleAIHandler(config_repo)

app = FastAPI(title="AI Detection Service - DDD")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# DTOs
class ToggleAIRequest(BaseModel):
    enabled: bool



class AIStatusResponse(BaseModel):
    camera_id: int
    ai_enabled: bool


# Endpoints
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai_detection"}


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



@app.get("/ai/status/{camera_id}", response_model=AIStatusResponse)
async def get_ai_status(camera_id: int):
    """Obtém status da IA para uma câmera"""
    config = config_repo.get(camera_id)
    
    return AIStatusResponse(
        camera_id=camera_id,
        ai_enabled=config.get('ai_enabled', True)
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
