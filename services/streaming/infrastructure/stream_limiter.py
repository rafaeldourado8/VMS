# services/streaming/infrastructure/stream_limiter.py
from redis import Redis
from typing import Optional

class StreamLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.limits = {"free": 1, "pro": 4, "enterprise": 4}
    
    def can_start_stream(self, user_id: str, plan: str) -> bool:
        key = f"streams:{user_id}"
        current = int(self.redis.get(key) or 0)
        return current < self.limits.get(plan, 1)
    
    def acquire_stream(self, user_id: str, camera_id: str) -> bool:
        key = f"streams:{user_id}"
        lock_key = f"stream_lock:{user_id}:{camera_id}"
        
        # Atomic check-and-increment
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 3600)  # Auto-cleanup
        pipe.setex(lock_key, 3600, "1")
        pipe.execute()
        return True
    
    def release_stream(self, user_id: str, camera_id: str):
        key = f"streams:{user_id}"
        lock_key = f"stream_lock:{user_id}:{camera_id}"
        
        pipe = self.redis.pipeline()
        pipe.decr(key)
        pipe.delete(lock_key)
        pipe.execute()
