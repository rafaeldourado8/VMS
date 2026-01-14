from dataclasses import dataclass
from datetime import datetime

@dataclass
class CityCreatedEvent:
    city_id: str
    name: str
    slug: str
    plan: str
    occurred_at: datetime
