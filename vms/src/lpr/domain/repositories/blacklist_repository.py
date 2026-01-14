from abc import ABC, abstractmethod
from domain.entities.blacklist_entry import BlacklistEntry

class IBlacklistRepository(ABC):
    @abstractmethod
    def save(self, entry: BlacklistEntry) -> None:
        pass
    
    @abstractmethod
    def find_by_plate(self, plate: str, city_id: str) -> BlacklistEntry | None:
        pass
    
    @abstractmethod
    def list_active(self, city_id: str) -> list[BlacklistEntry]:
        pass
    
    @abstractmethod
    def delete(self, entry_id: str) -> None:
        pass
