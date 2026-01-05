from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.stream import Stream


class StreamRepository(ABC):
    """Interface de repositório para Stream"""
    
    @abstractmethod
    def save(self, stream: Stream) -> Stream:
        """Salva ou atualiza um stream"""
        pass
    
    @abstractmethod
    def find_by_camera(self, camera_id: int) -> Optional[Stream]:
        """Busca stream por camera_id"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Stream]:
        """Lista todos os streams"""
        pass
    
    @abstractmethod
    def delete(self, camera_id: int) -> None:
        """Remove um stream"""
        pass
    
    @abstractmethod
    def exists(self, camera_id: int) -> bool:
        """Verifica se stream existe"""
        pass
