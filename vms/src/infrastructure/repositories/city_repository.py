from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

class CityRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, city_id: UUID):
        """Busca cidade por ID. Retorna None se não existir."""
        pass
    
    @abstractmethod
    def get_by_name(self, name: str):
        """Busca cidade por nome. Retorna None se não existir."""
        pass
    
    @abstractmethod
    def list_active(self) -> List:
        """Lista todas as cidades ativas."""
        pass
    
    @abstractmethod
    def exists(self, city_id: UUID) -> bool:
        """Verifica se cidade existe."""
        pass
