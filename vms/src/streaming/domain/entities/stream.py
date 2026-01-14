from dataclasses import dataclass
from datetime import datetime

@dataclass
class Stream:
    id: str
    camera_id: str
    hls_url: str
    status: str = 'stopped'
    started_at: datetime | None = None
    
    def start(self):
        self.status = 'active'
        self.started_at = datetime.now()
    
    def stop(self):
        self.status = 'stopped'
    
    def is_active(self) -> bool:
        return self.status == 'active'
