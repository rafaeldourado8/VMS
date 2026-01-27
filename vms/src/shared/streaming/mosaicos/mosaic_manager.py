from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from .models import Mosaic

class MosaicManager(ABC):
    
    @abstractmethod
    def create_mosaic(self, city_id: UUID, user_id: int) -> Mosaic:
        """Cria um novo mosaico."""
        pass
    
    @abstractmethod
    def get_mosaic(self, mosaic_id: str, city_id: UUID) -> Optional[Mosaic]:
        """Busca mosaico por ID."""
        pass
    
    @abstractmethod
    def add_stream_to_mosaic(self, mosaic_id: str, session_id: str, city_id: UUID) -> bool:
        """Adiciona stream ao mosaico (máx 4)."""
        pass
    
    @abstractmethod
    def remove_stream_from_mosaic(self, mosaic_id: str, session_id: str, city_id: UUID) -> bool:
        """Remove stream do mosaico."""
        pass
    
    @abstractmethod
    def delete_mosaic(self, mosaic_id: str, city_id: UUID) -> bool:
        """Deleta mosaico."""
        pass
