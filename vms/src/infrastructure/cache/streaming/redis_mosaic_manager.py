import json
from uuid import UUID, uuid4
from typing import Optional
import redis
from shared.streaming.mosaicos.mosaic_manager import MosaicManager
from shared.streaming.mosaicos.models import Mosaic

class RedisMosaicManager(MosaicManager):
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    def _mosaic_key(self, mosaic_id: str) -> str:
        return f"mosaic:{mosaic_id}"
    
    def _user_mosaics_key(self, user_id: int, city_id: UUID) -> str:
        return f"user:{user_id}:city:{city_id}:mosaics"
    
    def create_mosaic(self, city_id: UUID, user_id: int) -> Mosaic:
        mosaic_id = f"mosaic_{uuid4()}"
        
        mosaic = Mosaic(
            mosaic_id=mosaic_id,
            city_id=city_id,
            user_id=user_id,
            session_ids=[],
            max_streams=4
        )
        
        self.redis.setex(
            self._mosaic_key(mosaic_id),
            7200,  # TTL 2 horas
            json.dumps(mosaic.to_dict())
        )
        
        self.redis.sadd(self._user_mosaics_key(user_id, city_id), mosaic_id)
        
        return mosaic
    
    def get_mosaic(self, mosaic_id: str, city_id: UUID) -> Optional[Mosaic]:
        data = self.redis.get(self._mosaic_key(mosaic_id))
        if not data:
            return None
        
        mosaic_data = json.loads(data)
        
        if UUID(mosaic_data['city_id']) != city_id:
            return None
        
        return Mosaic(
            mosaic_id=mosaic_data['mosaic_id'],
            city_id=UUID(mosaic_data['city_id']),
            user_id=mosaic_data['user_id'],
            session_ids=mosaic_data['session_ids'],
            max_streams=mosaic_data['max_streams']
        )
    
    def add_stream_to_mosaic(self, mosaic_id: str, session_id: str, city_id: UUID) -> bool:
        mosaic = self.get_mosaic(mosaic_id, city_id)
        if not mosaic:
            return False
        
        if not mosaic.add_session(session_id):
            return False
        
        self.redis.setex(
            self._mosaic_key(mosaic_id),
            7200,
            json.dumps(mosaic.to_dict())
        )
        
        return True
    
    def remove_stream_from_mosaic(self, mosaic_id: str, session_id: str, city_id: UUID) -> bool:
        mosaic = self.get_mosaic(mosaic_id, city_id)
        if not mosaic:
            return False
        
        if not mosaic.remove_session(session_id):
            return False
        
        self.redis.setex(
            self._mosaic_key(mosaic_id),
            7200,
            json.dumps(mosaic.to_dict())
        )
        
        return True
    
    def delete_mosaic(self, mosaic_id: str, city_id: UUID) -> bool:
        mosaic = self.get_mosaic(mosaic_id, city_id)
        if not mosaic:
            return False
        
        self.redis.delete(self._mosaic_key(mosaic_id))
        self.redis.srem(self._user_mosaics_key(mosaic.user_id, city_id), mosaic_id)
        
        return True
