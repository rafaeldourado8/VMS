from abc import ABC, abstractmethod
from domain.entities.vehicle_search import VehicleSearch

class IVehicleSearchRepository(ABC):
    @abstractmethod
    def save(self, search: VehicleSearch) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, search_id: str) -> VehicleSearch | None:
        pass
    
    @abstractmethod
    def list_by_user(self, user_id: str) -> list[VehicleSearch]:
        pass
    
    @abstractmethod
    def list_by_city(self, city_id: str) -> list[VehicleSearch]:
        pass
    
    @abstractmethod
    def delete(self, search_id: str) -> None:
        pass
