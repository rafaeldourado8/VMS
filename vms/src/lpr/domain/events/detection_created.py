from dataclasses import dataclass
from datetime import datetime

@dataclass
class DetectionCreatedEvent:
    detection_id: str
    camera_id: str
    plate: str
    confidence: float
    is_blacklisted: bool
    occurred_at: datetime
