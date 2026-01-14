from abc import ABC, abstractmethod
from datetime import datetime
from domain.entities.detection import Detection

class IDetectionRepository(ABC):
    @abstractmethod
    def save(self, detection: Detection) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, detection_id: str) -> Detection | None:
        pass
    
    @abstractmethod
    def list_by_camera(self, camera_id: str, limit: int = 100) -> list[Detection]:
        pass
    
    @abstractmethod
    def list_by_plate(self, plate: str, city_id: str) -> list[Detection]:
        pass
    
    @abstractmethod
    def list_by_date_range(self, city_id: str, start: datetime, end: datetime) -> list[Detection]:
        pass
    
    @abstractmethod
    def count_by_camera(self, camera_id: str) -> int:
        pass
