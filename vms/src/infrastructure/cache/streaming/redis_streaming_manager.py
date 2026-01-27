import json
from datetime import datetime
from uuid import UUID
from typing import Optional
import redis
from shared.streaming.core.streaming_manager import StreamingManager
from shared.streaming.core.models import StreamingSession
from infrastructure.servers.mediamtx.adapter import MediaMTXAdapter
from infrastructure.repositories import DjangoCameraRepository

class RedisStreamingManager(StreamingManager):
    
    def __init__(self, redis_client: redis.Redis, mediamtx: MediaMTXAdapter, recording_adapter=None):
        self.redis = redis_client
        self.mediamtx = mediamtx
        self.camera_repo = DjangoCameraRepository()
        self.recording_adapter = recording_adapter
    
    def _session_key(self, session_id: str) -> str:
        return f"session:{session_id}"
    
    def _city_sessions_key(self, city_id: UUID) -> str:
        return f"city:{city_id}:sessions"
    
    def start_stream(self, camera_id: UUID, city_id: UUID, user_id: int) -> StreamingSession:
        camera = self.camera_repo.get_by_public_id(camera_id, city_id)
        if not camera:
            raise ValueError("Camera not found")
        
        if not camera.is_active:
            raise ValueError("Camera is not active")
        
        session_id = f"stream_{camera.public_id}"
        
        # REGRA 1: Backend NUNCA cria path - MediaMTX auto-gerencia
        # REGRA 2: path not found NÃO é erro - apenas registra sessão
        # REGRA 3: path not found = câmera OFFLINE (normal)
        
        session = StreamingSession(
            session_id=session_id,
            camera_id=camera.id,
            city_id=city_id,
            public_id=camera.public_id,
            user_id=user_id,
            started_at=datetime.utcnow(),
            protocol=camera.protocol
        )
        
        self.redis.setex(
            self._session_key(session_id),
            3600,
            json.dumps(session.to_dict())
        )
        
        self.redis.sadd(self._city_sessions_key(city_id), session_id)
        
        return session
    
    def stop_stream(self, session_id: str, city_id: UUID) -> bool:
        session = self.get_session(session_id, city_id)
        if not session:
            return False
        
        # REGRA 1: Backend NUNCA remove path - MediaMTX gerencia lifecycle
        # Path será destruído automaticamente quando fonte desconectar
        
        self.redis.delete(self._session_key(session_id))
        self.redis.srem(self._city_sessions_key(city_id), session_id)
        
        return True
    
    def get_session(self, session_id: str, city_id: UUID) -> Optional[StreamingSession]:
        data = self.redis.get(self._session_key(session_id))
        if not data:
            return None
        
        session_data = json.loads(data)
        
        if UUID(session_data['city_id']) != city_id:
            return None
        
        return StreamingSession(
            session_id=session_data['session_id'],
            camera_id=UUID(session_data['camera_id']),
            city_id=UUID(session_data['city_id']),
            public_id=UUID(session_data['public_id']),
            user_id=session_data['user_id'],
            started_at=datetime.fromisoformat(session_data['started_at']),
            protocol=session_data['protocol']
        )
    
    def list_active_sessions(self, city_id: UUID) -> list[StreamingSession]:
        session_ids = self.redis.smembers(self._city_sessions_key(city_id))
        sessions = []
        
        for session_id in session_ids:
            session = self.get_session(session_id.decode(), city_id)
            if session:
                sessions.append(session)
        
        return sessions
    
    def count_active_sessions(self, city_id: UUID) -> int:
        return self.redis.scard(self._city_sessions_key(city_id))
