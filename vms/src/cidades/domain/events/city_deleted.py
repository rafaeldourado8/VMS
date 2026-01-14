from dataclasses import dataclass
from datetime import datetime

@dataclass
class CityDeletedEvent:
    city_id: str
    slug: str
    occurred_at: datetime
