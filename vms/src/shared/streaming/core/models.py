from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class StreamingSession:
    session_id: str
    camera_id: UUID
    city_id: UUID
    public_id: UUID
    user_id: int
    started_at: datetime
    protocol: str
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'camera_id': str(self.camera_id),
            'city_id': str(self.city_id),
            'public_id': str(self.public_id),
            'user_id': self.user_id,
            'started_at': self.started_at.isoformat(),
            'protocol': self.protocol,
        }
