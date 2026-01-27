from uuid import UUID
from datetime import datetime
from typing import Optional
import redis
import json
from asgiref.sync import sync_to_async
from shared.streaming.recording.recording_manager import RecordingManager
from shared.streaming.recording.models import RecordingSession, RecordingStatus
from infrastructure.adapters.recording.mock_recording_adapter import MockRecordingAdapter
from infrastructure.repositories.camera_repository import CameraRepository

class RedisRecordingManager(RecordingManager):
    def __init__(self, redis_client: redis.Redis, recording_adapter: MockRecordingAdapter, camera_repo: CameraRepository):
        self.redis = redis_client
        self.adapter = recording_adapter
        self.camera_repo = camera_repo
    
    def enable_recording(self, camera_public_id: UUID, city_id: UUID) -> RecordingSession:
        camera = self.camera_repo.get_by_public_id(camera_public_id, city_id)
        if not camera or not camera.is_active:
            raise ValueError("Camera not found or inactive")
        
        stream_id = f"stream_{camera_public_id}"
        storage_path = f"/recordings/{stream_id}/"
        
        # MediaMTX grava automaticamente (record: yes global)
        # Backend apenas marca camera.recording_enabled = True
        
        session = RecordingSession(
            camera_id=camera.id,
            stream_id=stream_id,
            status=RecordingStatus.ON,
            started_at=datetime.now(),
            storage_path=storage_path,
            city_id=city_id
        )
        
        key = f"recording:{camera_public_id}"
        self.redis.setex(key, 86400, json.dumps(session.to_dict()))
        
        self.camera_repo.update_recording_status(camera.id, city_id, True)
        
        return session
    
    def disable_recording(self, camera_public_id: UUID, city_id: UUID) -> bool:
        camera = self.camera_repo.get_by_public_id(camera_public_id, city_id)
        if not camera:
            return False
        
        # MediaMTX para automaticamente quando fonte desconecta
        # Backend apenas marca camera.recording_enabled = False
        
        key = f"recording:{camera_public_id}"
        self.redis.delete(key)
        
        self.camera_repo.update_recording_status(camera.id, city_id, False)
        
        return True
    
    def get_status(self, camera_public_id: UUID, city_id: UUID) -> Optional[RecordingSession]:
        key = f"recording:{camera_public_id}"
        data = self.redis.get(key)
        
        if not data:
            return None
        
        session_dict = json.loads(data)
        return RecordingSession(
            camera_id=UUID(session_dict['camera_id']),
            stream_id=session_dict['stream_id'],
            status=RecordingStatus(session_dict['status']),
            started_at=datetime.fromisoformat(session_dict['started_at']),
            storage_path=session_dict['storage_path'],
            city_id=UUID(session_dict['city_id'])
        )
