from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.camera import Camera


class CameraRepository(ABC):
    """Interface de repositório para Camera"""
    
    @abstractmethod
    def save(self, camera: Camera) -> Camera:
        """Salva ou atualiza uma câmera"""
        pass
    
    @abstractmethod
    def find_by_id(self, camera_id: int) -> Optional[Camera]:
        """Busca câmera por ID"""
        pass
    
    @abstractmethod
    def find_by_owner(self, owner_id: int) -> List[Camera]:
        """Busca câmeras por proprietário"""
        pass
    
    @abstractmethod
    def delete(self, camera_id: int) -> None:
        """Remove uma câmera"""
        pass
    
    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """Verifica se existe câmera com o nome"""
        pass
