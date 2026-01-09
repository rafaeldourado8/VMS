# services/streaming/infrastructure/snapshot_cache.py
from redis import Redis
from typing import Optional
import base64

class SnapshotCache:
    def __init__(self, redis: Redis, ttl: int = 30):
        self.redis = redis
        self.ttl = ttl  # 30 seconds default
    
    def get(self, camera_id: str) -> Optional[bytes]:
        key = f"snapshot:{camera_id}"
        data = self.redis.get(key)
        return base64.b64decode(data) if data else None
    
    def set(self, camera_id: str, image_bytes: bytes):
        key = f"snapshot:{camera_id}"
        encoded = base64.b64encode(image_bytes)
        self.redis.setex(key, self.ttl, encoded)
    
    def invalidate(self, camera_id: str):
        self.redis.delete(f"snapshot:{camera_id}")
