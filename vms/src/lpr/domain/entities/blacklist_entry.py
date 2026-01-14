from dataclasses import dataclass
from datetime import datetime

@dataclass
class BlacklistEntry:
    id: str
    plate: str
    reason: str
    city_id: str
    created_at: datetime
    is_active: bool = True
    
    def matches(self, plate: str) -> bool:
        return self.is_active and self.plate.upper() == plate.upper()
    
    def deactivate(self):
        self.is_active = False
