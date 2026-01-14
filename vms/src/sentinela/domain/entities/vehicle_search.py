from dataclasses import dataclass
from datetime import datetime

@dataclass
class VehicleSearch:
    id: str
    city_id: str
    user_id: str
    plate: str | None
    color: str | None
    vehicle_type: str | None
    start_date: datetime
    end_date: datetime
    status: str = 'pending'  # pending, processing, completed, failed
    created_at: datetime | None = None
    error_message: str | None = None
    
    def start_processing(self):
        self.status = 'processing'
    
    def complete(self):
        self.status = 'completed'
    
    def fail(self, error: str):
        self.status = 'failed'
        self.error_message = error
    
    def is_completed(self) -> bool:
        return self.status == 'completed'
