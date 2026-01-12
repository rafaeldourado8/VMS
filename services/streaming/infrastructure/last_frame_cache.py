from redis import Redis
from typing import Optional
import base64
import time

class LastFrameCache:
    """Cache last frame in Redis with 5 min TTL"""
    
    def __init__(self, redis: Redis, ttl: int = 300):
        self.redis = redis
        self.ttl = ttl
    
    def set(self, camera_id: int, frame_bytes: bytes):
        """Store last frame"""
        key = f"last_frame:{camera_id}"
        encoded = base64.b64encode(frame_bytes).decode('utf-8')
        self.redis.setex(key, self.ttl, encoded)
    
    def get(self, camera_id: int) -> Optional[bytes]:
        """Get last frame"""
        key = f"last_frame:{camera_id}"
        data = self.redis.get(key)
        if data:
            return base64.b64decode(data)
        return None
    
    def delete(self, camera_id: int):
        """Delete cached frame"""
        self.redis.delete(f"last_frame:{camera_id}")
