from uuid import UUID
from typing import Dict, Any
from asgiref.sync import sync_to_async
from shared.streaming.recording.recording_manager import RecordingManager
from infrastructure.servers.mediamtx.adapter import MediaMTXAdapter
from infrastructure.repositories.camera_repository import CameraRepository

class MediaMTXRecordingManager(RecordingManager):
    def __init__(self, mediamtx_adapter: MediaMTXAdapter, camera_repo: CameraRepository):
        self.mediamtx = mediamtx_adapter
        self.camera_repo = camera_repo
    
    async def enable_recording(self, camera_id: UUID, city_id: UUID) -> bool:
        camera = await sync_to_async(self.camera_repo.get_by_id)(camera_id, city_id)
        if not camera or not camera.is_active:
            return False
        
        path_name = f"stream_{camera_id}"
        config = {
            "record": True,
            "recordPath": f"/recordings/{city_id}/{camera_id}/%Y-%m-%d_%H-%M-%S",
            "recordFormat": "fmp4",
            "recordPartDuration": "4s",
            "recordSegmentDuration": "30m",
            "recordDeleteAfter": "7d"
        }
        
        success = await sync_to_async(self.mediamtx.update_path_config)(path_name, config)
        if success:
            await sync_to_async(self.camera_repo.update_recording_status)(camera_id, city_id, True)
        
        return success
    
    async def disable_recording(self, camera_id: UUID, city_id: UUID) -> bool:
        camera = await sync_to_async(self.camera_repo.get_by_id)(camera_id, city_id)
        if not camera:
            return False
        
        path_name = f"stream_{camera_id}"
        config = {"record": False}
        
        success = await sync_to_async(self.mediamtx.update_path_config)(path_name, config)
        if success:
            await sync_to_async(self.camera_repo.update_recording_status)(camera_id, city_id, False)
        
        return success
    
    async def get_recording_status(self, camera_id: UUID, city_id: UUID) -> Dict[str, Any]:
        camera = await sync_to_async(self.camera_repo.get_by_id)(camera_id, city_id)
        if not camera:
            return {"enabled": False, "error": "Camera not found"}
        
        path_name = f"stream_{camera_id}"
        path_info = await sync_to_async(self.mediamtx.get_path)(path_name)
        
        return {
            "camera_id": str(camera_id),
            "enabled": camera.recording_enabled,
            "active": path_info is not None,
            "path": f"/recordings/{city_id}/{camera_id}/"
        }
