from dataclasses import dataclass
from datetime import datetime

@dataclass
class CameraActivatedEvent:
    camera_id: str
    occurred_at: datetime
