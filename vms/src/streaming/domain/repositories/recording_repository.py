from abc import ABC, abstractmethod
from datetime import datetime
from domain.entities.recording import Recording

class IRecordingRepository(ABC):
    @abstractmethod
    def save(self, recording: Recording) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, recording_id: str) -> Recording | None:
        pass
    
    @abstractmethod
    def list_by_camera(self, camera_id: str) -> list[Recording]:
        pass
    
    @abstractmethod
    def list_by_date_range(self, city_id: str, start: datetime, end: datetime) -> list[Recording]:
        pass
    
    @abstractmethod
    def list_expiring_soon(self, retention_days: int, days_before: int = 1) -> list[Recording]:
        pass
    
    @abstractmethod
    def delete(self, recording_id: str) -> None:
        pass
