import redis
import logging
import difflib

class DedupCache:
    def __init__(self, host='redis', port=6379, ttl=300):
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.ttl = ttl
        self.logger = logging.getLogger(__name__)
    
    def is_duplicate(self, camera_id: int, plate: str) -> bool:
        key = f"plate:{camera_id}:{plate}"
        
        # Verifica exata
        if self.client.exists(key):
            return True
        
        # Verifica similar (80%)
        pattern = f"plate:{camera_id}:*"
        for existing_key in self.client.scan_iter(match=pattern):
            existing_plate = existing_key.split(':')[-1]
            similarity = difflib.SequenceMatcher(None, plate, existing_plate).ratio()
            if similarity > 0.8:
                return True
        
        return False
    
    def add(self, camera_id: int, plate: str):
        key = f"plate:{camera_id}:{plate}"
        self.client.setex(key, self.ttl, "1")
