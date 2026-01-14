from dataclasses import dataclass
from datetime import datetime

@dataclass
class TrajectoryPoint:
    camera_id: str
    camera_name: str
    timestamp: datetime
    image_url: str
    confidence: float
    location: str | None = None
    
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.9
