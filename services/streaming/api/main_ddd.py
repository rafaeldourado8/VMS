"""
Streaming Service API - Refatorado com DDD
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from application.streaming.commands.provision_stream_command import ProvisionStreamCommand
from application.streaming.commands.remove_stream_command import RemoveStreamCommand
from application.streaming.handlers.provision_stream_handler import ProvisionStreamHandler
from application.streaming.handlers.remove_stream_handler import RemoveStreamHandler
from infrastructure.repositories.in_memory_stream_repository import InMemoryStreamRepository
from infrastructure.mediamtx.mediamtx_client import MediaMTXClient
from domain.streaming.exceptions import StreamAlreadyExistsException, StreamNotFoundException

# Inicialização
repository = InMemoryStreamRepository()
mediamtx_client = MediaMTXClient()
provision_handler = ProvisionStreamHandler(repository, base_url="http://localhost:8889")
remove_handler = RemoveStreamHandler(repository)

app = FastAPI(title="Streaming Service - DDD")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# DTOs
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
    message: str = ""


# Endpoints
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/cameras/provision", response_model=ProvisionResponse)
async def provision(request: ProvisionRequest):
    """Provisiona um stream usando DDD handler"""
    try:
        command = ProvisionStreamCommand(
            camera_id=request.camera_id,
            rtsp_url=request.rtsp_url,
            name=request.name,
            on_demand=request.on_demand
        )
        
        stream = provision_handler.handle(command)
        
        # Provisiona no MediaMTX
        success = mediamtx_client.add_path(
            str(stream.path),
            stream.rtsp_url,
            stream.on_demand
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Falha ao provisionar no MediaMTX")
        
        return ProvisionResponse(
            success=True,
            camera_id=stream.camera_id,
            stream_path=str(stream.path),
            hls_url=str(stream.hls_url),
            message="Stream provisionado com sucesso"
        )
        
    except StreamAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/cameras/{camera_id}")
async def remove_camera(camera_id: int):
    """Remove um stream usando DDD handler"""
    try:
        command = RemoveStreamCommand(camera_id=camera_id)
        remove_handler.handle(command)
        
        # Remove do MediaMTX
        mediamtx_client.remove_path(f"cam_{camera_id}")
        
        return {"success": True, "message": "Stream removido"}
        
    except StreamNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cameras/{camera_id}/status")
async def camera_status(camera_id: int):
    """Obtém status de um stream"""
    stream = repository.find_by_camera(camera_id)
    
    if not stream:
        raise HTTPException(status_code=404, detail="Stream não encontrado")
    
    # Obtém status do MediaMTX
    mtx_status = mediamtx_client.get_path_status(str(stream.path))
    
    return {
        "camera_id": stream.camera_id,
        "status": stream.status.value,
        "viewers": stream.viewers,
        "hls_url": str(stream.hls_url),
        "mediamtx_ready": mtx_status.get("ready", False) if mtx_status else False
    }


@app.get("/streams")
async def list_streams():
    """Lista todos os streams"""
    streams = repository.find_all()
    
    return [
        {
            "camera_id": s.camera_id,
            "path": str(s.path),
            "status": s.status.value,
            "viewers": s.viewers,
            "hls_url": str(s.hls_url)
        }
        for s in streams
    ]
