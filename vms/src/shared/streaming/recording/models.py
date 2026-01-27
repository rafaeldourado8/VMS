from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum

class RecordingStatus(str, Enum):
    ON = "ON"
    OFF = "OFF"

@dataclass
class RecordingSession:
    camera_id: UUID
    stream_id: str
    status: RecordingStatus
    started_at: datetime
    storage_path: str
    city_id: UUID
    
    def to_dict(self):
        return {
            'camera_id': str(self.camera_id),
            'stream_id': self.stream_id,
            'status': self.status.value,
            'started_at': self.started_at.isoformat(),
            'storage_path': self.storage_path,
            'city_id': str(self.city_id)
        }
