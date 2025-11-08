# fastapi_services/streaming/app/api/streaming.py
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import List
import logging
import asyncio

from ..schemas import StreamConfig, StreamInfo, StreamResponse
from ..services.stream_manager import StreamManager
from ..core.dependencies import get_stream_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/start/{camera_id}", response_model=StreamResponse)
async def start_stream(
    camera_id: str,
    config: StreamConfig,
    stream_service: StreamManager = Depends(get_stream_service)
):
    """Inicia um stream"""
    try:
        if stream_service.stream_exists(camera_id):
            raise HTTPException(status_code=400, detail="Stream já existe")
        
        success = await stream_service.create_stream(camera_id, config)
        
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao iniciar stream")
        
        return StreamResponse(
            success=True,
            message=f"Stream iniciado: {camera_id}",
            camera_id=camera_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao iniciar stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop/{camera_id}", response_model=StreamResponse)
async def stop_stream(
    camera_id: str,
    stream_service: StreamManager = Depends(get_stream_service)
):
    """Para um stream"""
    try:
        success = await stream_service.stop_stream(camera_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Stream não encontrado")
        
        return StreamResponse(
            success=True,
            message=f"Stream parado: {camera_id}",
            camera_id=camera_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao parar stream: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info/{camera_id}", response_model=StreamInfo)
async def get_stream_info(
    camera_id: str,
    stream_service: StreamManager = Depends(get_stream_service)
):
    """Obtém informações de um stream"""
    info = stream_service.get_stream_info(camera_id)
    
    if not info:
        raise HTTPException(status_code=404, detail="Stream não encontrado")
    
    return info

@router.get("/list", response_model=List[StreamInfo])
async def list_streams(
    stream_service: StreamManager = Depends(get_stream_service)
):
    """Lista todos os streams"""
    return stream_service.list_streams()

@router.get("/mjpeg/{camera_id}")
async def stream_mjpeg(
    camera_id: str,
    stream_service: StreamManager = Depends(get_stream_service)
):
    """Stream MJPEG via HTTP"""
    if not stream_service.stream_exists(camera_id):
        raise HTTPException(status_code=404, detail="Stream não encontrado")
    
    async def generate():
        """Gerador de frames"""
        try:
            while True:
                frame = await stream_service.get_frame(camera_id)
                
                if frame is None:
                    await asyncio.sleep(0.01)
                    continue
                
                yield frame
                await asyncio.sleep(0.033)  # ~30 FPS
                
        except Exception as e:
            logger.error(f"Erro no stream: {str(e)}")
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.websocket("/ws/{camera_id}")
async def websocket_stream(
    websocket: WebSocket,
    camera_id: str,
    stream_service: StreamManager = Depends(get_stream_service)
):
    """Stream via WebSocket"""
    await websocket.accept()
    
    if not stream_service.stream_exists(camera_id):
        await websocket.close(code=1008, reason="Stream não encontrado")
        return
    
    try:
        while True:
            frame = await stream_service.get_frame(camera_id)
            
            if frame is None:
                await asyncio.sleep(0.01)
                continue
            
            # Envia frame como bytes
            await websocket.send_bytes(frame)
            await asyncio.sleep(0.033)  # ~30 FPS
            
    except WebSocketDisconnect:
        logger.info(f"Cliente desconectado: {camera_id}")
    except Exception as e:
        logger.error(f"Erro no WebSocket: {str(e)}")
        await websocket.close(code=1011, reason=str(e))