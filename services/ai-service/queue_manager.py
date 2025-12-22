import asyncio
import redis.asyncio as aioredis
import json
import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)

class QueueManager:
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.queue_key = "ai:detection_queue"
        self.result_key_prefix = "ai:result:"
        
    async def connect(self):
        self.redis = await aioredis.from_url(
            f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
            password=settings.redis_password if settings.redis_password else None,
            decode_responses=False
        )
        logger.info("Connected to Redis")
    
    async def disconnect(self):
        if self.redis:
            await self.redis.close()
    
    async def enqueue(self, camera_id: int, image_data: bytes) -> str:
        task_id = f"{camera_id}_{asyncio.get_event_loop().time()}"
        task = {
            "task_id": task_id,
            "camera_id": camera_id,
            "image_data": image_data.hex()
        }
        
        queue_size = await self.redis.llen(self.queue_key)
        if queue_size >= settings.max_queue_size:
            raise Exception("Queue full")
        
        await self.redis.rpush(self.queue_key, json.dumps(task))
        return task_id
    
    async def dequeue(self) -> Optional[dict]:
        data = await self.redis.blpop(self.queue_key, timeout=1)
        if data:
            return json.loads(data[1])
        return None
    
    async def store_result(self, task_id: str, result: dict, ttl: int = 300):
        key = f"{self.result_key_prefix}{task_id}"
        await self.redis.setex(key, ttl, json.dumps(result))
    
    async def get_result(self, task_id: str) -> Optional[dict]:
        key = f"{self.result_key_prefix}{task_id}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def get_queue_size(self) -> int:
        return await self.redis.llen(self.queue_key)
