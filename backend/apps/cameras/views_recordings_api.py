from ninja import Router
from typing import List
from datetime import datetime
from pydantic import BaseModel

router = Router(tags=["Recordings"])

class RecordingSchema(BaseModel):
    id: int
    camera_id: int
    camera_name: str
    video_path: str
    snapshot_url: str | None
    duration_seconds: int
    file_size_mb: float
    started_at: datetime
    ended_at: datetime | None

@router.get("/recordings", response=List[RecordingSchema])
async def list_recordings(request, camera_id: int = None, limit: int = 50):
    """Lista gravações com snapshots em cache."""
    from apps.cameras.models_recording import Recording
    
    qs = Recording.objects.select_related('camera')
    
    if camera_id:
        qs = qs.filter(camera_id=camera_id)
    
    recordings = []
    async for rec in qs[:limit]:
        recordings.append(RecordingSchema(
            id=rec.id,
            camera_id=rec.camera_id,
            camera_name=rec.camera.name,
            video_path=rec.video_path,
            snapshot_url=rec.snapshot_cached.url if rec.snapshot_cached else None,
            duration_seconds=rec.duration_seconds,
            file_size_mb=round(rec.file_size_bytes / 1024 / 1024, 2),
            started_at=rec.started_at,
            ended_at=rec.ended_at
        ))
    
    return recordings

@router.post("/recordings/{recording_id}/generate-snapshot")
async def generate_snapshot(request, recording_id: int):
    """Gera snapshot em cache para uma gravação."""
    from apps.cameras.services_snapshot import SnapshotCacheService
    
    success = await SnapshotCacheService.cache_recording_snapshot(recording_id)
    return {"success": success}
