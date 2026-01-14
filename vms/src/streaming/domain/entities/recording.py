from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Recording:
    id: str
    camera_id: str
    file_path: str
    started_at: datetime
    ended_at: datetime | None = None
    size_bytes: int = 0
    is_permanent: bool = False
    
    def should_delete(self, retention_days: int) -> bool:
        if self.is_permanent:
            return False
        
        age = datetime.now() - self.started_at
        return age.days >= retention_days
    
    def expires_in_days(self, retention_days: int) -> int:
        if self.is_permanent:
            return -1
        
        age = datetime.now() - self.started_at
        return max(0, retention_days - age.days)
    
    def mark_as_permanent(self):
        self.is_permanent = True
