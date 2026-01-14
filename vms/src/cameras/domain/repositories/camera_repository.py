from abc import ABC, abstractmethod
from domain.entities.camera import Camera

class ICameraRepository(ABC):
    @abstractmethod
    def save(self, camera: Camera) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, camera_id: str) -> Camera | None:
        pass
    
    @abstractmethod
    def list_by_city(self, city_id: str) -> list[Camera]:
        pass
    
    @abstractmethod
    def count_by_city(self, city_id: str) -> int:
        pass
    
    @abstractmethod
    def count_lpr_by_city(self, city_id: str) -> int:
        pass
    
    @abstractmethod
    def delete(self, camera_id: str) -> None:
        pass
