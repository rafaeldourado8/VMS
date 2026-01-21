"""
API FastAPI para controle dinâmico de câmeras
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Detection API")

# Gerenciador global de agentes (será injetado pelo main.py)
agent_manager = None

class StartCameraRequest(BaseModel):
    pass  # Vazio - busca do backend

@app.get("/health")
async def health():
    return {"status": "ok", "active_cameras": len(agent_manager.active_agents) if agent_manager else 0}

@app.post("/cameras/{camera_id}/start")
async def start_camera(camera_id: int):
    """Inicia detecção para uma câmera"""
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    try:
        agent_manager.start_camera(camera_id)
        return {"success": True, "camera_id": camera_id, "message": "Camera started"}
    except Exception as e:
        logger.error(f"Error starting camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cameras/{camera_id}/stop")
async def stop_camera(camera_id: int):
    """Para detecção para uma câmera"""
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    try:
        agent_manager.stop_camera(camera_id)
        return {"success": True, "camera_id": camera_id, "message": "Camera stopped"}
    except Exception as e:
        logger.error(f"Error stopping camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cameras")
async def list_cameras():
    """Lista câmeras ativas"""
    if not agent_manager:
        return {"cameras": []}
    
    return {
        "cameras": [
            {"camera_id": agent.camera_id, "rtsp_url": agent.rtsp_url}
            for agent in agent_manager.active_agents.values()
        ]
    }
