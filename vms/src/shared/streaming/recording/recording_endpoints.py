from fastapi import Header, HTTPException
from uuid import UUID
from asgiref.sync import sync_to_async

async def enable_recording(
    camera_id: UUID,
    recording_manager,
    x_city_id: UUID = Header(..., alias="X-City-ID"),
    x_user_id: int = Header(..., alias="X-User-ID")
):
    try:
        session = await sync_to_async(recording_manager.enable_recording)(camera_id, x_city_id)
        return {
            "camera_id": str(camera_id),
            "stream_id": session.stream_id,
            "status": session.status.value,
            "storage_path": session.storage_path,
            "started_at": session.started_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

async def disable_recording(
    camera_id: UUID,
    recording_manager,
    x_city_id: UUID = Header(..., alias="X-City-ID"),
    x_user_id: int = Header(..., alias="X-User-ID")
):
    success = await sync_to_async(recording_manager.disable_recording)(camera_id, x_city_id)
    if not success:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    return {
        "camera_id": str(camera_id),
        "status": "OFF",
        "message": "Recording disabled"
    }

async def get_recording_status(
    camera_id: UUID,
    recording_manager,
    x_city_id: UUID = Header(..., alias="X-City-ID"),
    x_user_id: int = Header(..., alias="X-User-ID")
):
    session = await sync_to_async(recording_manager.get_status)(camera_id, x_city_id)
    
    if not session:
        return {
            "camera_id": str(camera_id),
            "status": "OFF",
            "recording": False
        }
    
    return {
        "camera_id": str(camera_id),
        "stream_id": session.stream_id,
        "status": session.status.value,
        "storage_path": session.storage_path,
        "started_at": session.started_at.isoformat(),
        "recording": session.status == "ON"
    }
