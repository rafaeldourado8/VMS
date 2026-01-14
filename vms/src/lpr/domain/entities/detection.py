from dataclasses import dataclass
from datetime import datetime

@dataclass
class Detection:
    id: str
    camera_id: str
    plate: str
    confidence: float
    image_url: str
    detected_at: datetime
    city_id: str
    
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.9
    
    def is_valid_confidence(self) -> bool:
        return self.confidence >= 0.75
