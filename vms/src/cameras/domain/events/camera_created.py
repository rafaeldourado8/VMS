from dataclasses import dataclass
from datetime import datetime

@dataclass
class CameraCreatedEvent:
    camera_id: str
    name: str
    type: str
    city_id: str
    occurred_at: datetime
