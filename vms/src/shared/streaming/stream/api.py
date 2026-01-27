import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from fastapi import FastAPI, Header, HTTPException, status
from uuid import UUID
import redis
import asyncio
from datetime import datetime
from asgiref.sync import sync_to_async
from infrastructure.cache.streaming import RedisStreamingManager
from infrastructure.cache.streaming.redis_mosaic_manager import RedisMosaicManager
from infrastructure.cache.streaming.redis_recording_manager import RedisRecordingManager
from infrastructure.adapters.recording.mediamtx_recording_adapter import MediaMTXRecordingAdapter
from infrastructure.servers.mediamtx import HTTPMediaMTXAdapter
from infrastructure.repositories.django_camera_repository import DjangoCameraRepository
from infrastructure.observers.path_observer import PathObserver
from shared.streaming.stream.schemas import (
    StreamStartResponse,
    StreamStopResponse,
    StreamListResponse,
    StreamSessionResponse,
    RecordingEnableResponse,
    RecordingDisableResponse,
    RecordingStatusResponse,
    MosaicCreateResponse,
    MosaicResponse,
    MosaicAddStreamResponse,
    MosaicRemoveStreamResponse,
    MosaicDeleteResponse,
    HealthResponse
)

app = FastAPI(
    title="VMS Streaming API",
    version="1.0.0",
    description="API para gerenciamento de streaming, gravação e mosaicos"
)

redis_client = redis.Redis(host='redis', port=6379, decode_responses=False)
mediamtx = HTTPMediaMTXAdapter()
camera_repo = DjangoCameraRepository()
recording_adapter = MediaMTXRecordingAdapter(mediamtx)
streaming_manager = RedisStreamingManager(redis_client, mediamtx, recording_adapter)
mosaic_manager = RedisMosaicManager(redis_client)
recording_manager = RedisRecordingManager(redis_client, recording_adapter, camera_repo)
path_observer = PathObserver(mediamtx, camera_repo, interval=10)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(path_observer.start())

@app.on_event("shutdown")
async def shutdown_event():
    await path_observer.stop()

@app.post(
    "/api/v1/streams",
    response_model=StreamStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Iniciar stream",
    tags=["Streaming"]
)
async def start_stream(
    camera_id: UUID,
    x_city_id: UUID = Header(..., alias="X-City-ID"),
    x_user_id: int = Header(..., alias="X-User-ID")
):
    """Inicia streaming de uma câmera. Backend apenas registra sessão, MediaMTX gerencia path."""
    try:
        session = await sync_to_async(streaming_manager.start_stream)(camera_id, x_city_id, x_user_id)
        return StreamStartResponse(
            session_id=session.session_id,
            camera_id=session.camera_id,
            hls_url=mediamtx.get_hls_url(session.session_id),
            started_at=session.started_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.delete(
    "/api/v1/streams/{session_id}",
    response_model=StreamStopResponse,
    summary="Parar stream",
    tags=["Streaming"]
)
async def stop_stream(
    session_id: str,
    x_city_id: UUID = Header(..., alias="X-City-ID")
):
    """Para streaming de uma sessão. Backend apenas remove sessão, MediaMTX gerencia path."""
    stopped = await sync_to_async(streaming_manager.stop_stream)(session_id, x_city_id)
    if not stopped:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return StreamStopResponse(session_id=session_id, stopped_at=datetime.utcnow())

@app.get(
    "/api/v1/streams",
    response_model=StreamListResponse,
    summary="Listar streams ativos",
    tags=["Streaming"]
)
async def list_streams(x_city_id: UUID = Header(..., alias="X-City-ID")):
    """Lista todas as sessões de streaming ativas da cidade."""
    sessions = await sync_to_async(streaming_manager.list_active_sessions)(x_city_id)
    return StreamListResponse(
        count=len(sessions),
        sessions=[
            StreamSessionResponse(
                session_id=s.session_id,
                camera_id=s.camera_id,
                public_id=s.public_id,
                protocol=s.protocol,
                started_at=s.started_at,
                hls_url=mediamtx.get_hls_url(s.session_id)
            )
            for s in sessions
        ]
    )

@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["System"]
)
async def health():
    """Verifica saúde da API e dependências."""
    mediamtx_ok = mediamtx.get_all_paths() is not None
    redis_ok = redis_client.ping()
    
    return HealthResponse(
        status="healthy" if (mediamtx_ok and redis_ok) else "degraded",
        mediamtx=mediamtx_ok,
        redis=redis_ok
    )

# Mosaic endpoints
@app.post(
    "/api/v1/mosaics",
    response_model=MosaicCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar mosaico",
    tags=["Mosaics"]
)
async def create_mosaic(
    x_city_id: UUID = Header(..., alias="X-City-ID"),
    x_user_id: int = Header(..., alias="X-User-ID")
):
    """Cria um novo mosaico (máx 4 streams)."""
    mosaic = await sync_to_async(mosaic_manager.create_mosaic)(x_city_id, x_user_id)
    return MosaicCreateResponse(
        mosaic_id=mosaic.mosaic_id,
        city_id=mosaic.city_id,
        user_id=mosaic.user_id,
        max_streams=mosaic.max_streams,
        current_streams=len(mosaic.session_ids)
    )

@app.get(
    "/api/v1/mosaics/{mosaic_id}",
    response_model=MosaicResponse,
    summary="Obter mosaico",
    tags=["Mosaics"]
)
async def get_mosaic(
    mosaic_id: str,
    x_city_id: UUID = Header(..., alias="X-City-ID")
):
    """Retorna detalhes de um mosaico."""
    mosaic = await sync_to_async(mosaic_manager.get_mosaic)(mosaic_id, x_city_id)
    if not mosaic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mosaic not found")
    return MosaicResponse(
        mosaic_id=mosaic.mosaic_id,
        city_id=mosaic.city_id,
        user_id=mosaic.user_id,
        session_ids=mosaic.session_ids,
        max_streams=mosaic.max_streams,
        current_streams=len(mosaic.session_ids)
    )

@app.post(
    "/api/v1/mosaics/{mosaic_id}/streams/{session_id}",
    response_model=MosaicAddStreamResponse,
    summary="Adicionar stream ao mosaico",
    tags=["Mosaics"]
)
async def add_stream_to_mosaic(
    mosaic_id: str,
    session_id: str,
    x_city_id: UUID = Header(..., alias="X-City-ID")
):
    """Adiciona um stream ao mosaico (máx 4)."""
    added = await sync_to_async(mosaic_manager.add_stream_to_mosaic)(mosaic_id, session_id, x_city_id)
    if not added:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot add stream (max 4 or mosaic not found)")
    
    mosaic = await sync_to_async(mosaic_manager.get_mosaic)(mosaic_id, x_city_id)
    return MosaicAddStreamResponse(
        mosaic_id=mosaic_id,
        session_id=session_id,
        current_streams=len(mosaic.session_ids)
    )

@app.delete(
    "/api/v1/mosaics/{mosaic_id}/streams/{session_id}",
    response_model=MosaicRemoveStreamResponse,
    summary="Remover stream do mosaico",
    tags=["Mosaics"]
)
async def remove_stream_from_mosaic(
    mosaic_id: str,
    session_id: str,
    x_city_id: UUID = Header(..., alias="X-City-ID")
):
    """Remove um stream do mosaico."""
    removed = await sync_to_async(mosaic_manager.remove_stream_from_mosaic)(mosaic_id, session_id, x_city_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stream or mosaic not found")
    
    mosaic = await sync_to_async(mosaic_manager.get_mosaic)(mosaic_id, x_city_id)
    return MosaicRemoveStreamResponse(
        mosaic_id=mosaic_id,
        session_id=session_id,
        current_streams=len(mosaic.session_ids)
    )

@app.delete(
    "/api/v1/mosaics/{mosaic_id}",
    response_model=MosaicDeleteResponse,
    summary="Deletar mosaico",
    tags=["Mosaics"]
)
async def delete_mosaic(
    mosaic_id: str,
    x_city_id: UUID = Header(..., alias="X-City-ID")
):
    """Deleta um mosaico."""
    deleted = await sync_to_async(mosaic_manager.delete_mosaic)(mosaic_id, x_city_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mosaic not found")
    return MosaicDeleteResponse(mosaic_id=mosaic_id)

@app.put(
    "/api/v1/cameras/{camera_id}/recording",
    response_model=RecordingEnableResponse,
    summary="Habilitar gravação",
    tags=["Recording"]
)
async def enable_recording(
    camera_id: UUID,
    x_city_id: UUID = Header(..., alias="X-City-ID"),
    x_user_id: int = Header(..., alias="X-User-ID")
):
    """Habilita gravação para uma câmera. MediaMTX grava automaticamente."""
    try:
        session = await sync_to_async(recording_manager.enable_recording)(camera_id, x_city_id)
        return RecordingEnableResponse(
            camera_id=session.camera_id,
            storage_path=session.storage_path,
            enabled_at=session.started_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.delete(
    "/api/v1/cameras/{camera_id}/recording",
    response_model=RecordingDisableResponse,
    summary="Desabilitar gravação",
    tags=["Recording"]
)
async def disable_recording(
    camera_id: UUID,
    x_city_id: UUID = Header(..., alias="X-City-ID"),
    x_user_id: int = Header(..., alias="X-User-ID")
):
    """Desabilita gravação para uma câmera."""
    success = await sync_to_async(recording_manager.disable_recording)(camera_id, x_city_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return RecordingDisableResponse(camera_id=camera_id, disabled_at=datetime.utcnow())

@app.get(
    "/api/v1/cameras/{camera_id}/recording",
    response_model=RecordingStatusResponse,
    summary="Status da gravação",
    tags=["Recording"]
)
async def get_recording_status(
    camera_id: UUID,
    x_city_id: UUID = Header(..., alias="X-City-ID"),
    x_user_id: int = Header(..., alias="X-User-ID")
):
    """Retorna status da gravação de uma câmera."""
    session = await sync_to_async(recording_manager.get_status)(camera_id, x_city_id)
    
    if not session:
        return RecordingStatusResponse(camera_id=camera_id, recording=False)
    
    return RecordingStatusResponse(
        camera_id=session.camera_id,
        recording=session.status == "ON",
        storage_path=session.storage_path,
        started_at=session.started_at
    )
