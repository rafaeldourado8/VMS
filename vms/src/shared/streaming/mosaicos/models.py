from dataclasses import dataclass
from uuid import UUID
from typing import List

@dataclass
class Mosaic:
    mosaic_id: str
    city_id: UUID
    user_id: int
    session_ids: List[str]
    max_streams: int = 4
    
    def can_add_stream(self) -> bool:
        return len(self.session_ids) < self.max_streams
    
    def add_session(self, session_id: str) -> bool:
        if not self.can_add_stream():
            return False
        if session_id not in self.session_ids:
            self.session_ids.append(session_id)
            return True
        return False
    
    def remove_session(self, session_id: str) -> bool:
        if session_id in self.session_ids:
            self.session_ids.remove(session_id)
            return True
        return False
    
    def to_dict(self):
        return {
            'mosaic_id': self.mosaic_id,
            'city_id': str(self.city_id),
            'user_id': self.user_id,
            'session_ids': self.session_ids,
            'max_streams': self.max_streams,
            'current_streams': len(self.session_ids)
        }
