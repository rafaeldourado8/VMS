from abc import ABC, abstractmethod
from domain.entities.city import City

class ICityRepository(ABC):
    @abstractmethod
    def save(self, city: City) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, city_id: str) -> City | None:
        pass
    
    @abstractmethod
    def find_by_slug(self, slug: str) -> City | None:
        pass
    
    @abstractmethod
    def list_all(self) -> list[City]:
        pass
    
    @abstractmethod
    def delete(self, city_id: str) -> None:
        pass
