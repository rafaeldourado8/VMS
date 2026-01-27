from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

class CameraRepository(ABC):
    
    @abstractmethod
    def get_by_id(self, camera_id: UUID, city_id: UUID):
        """Busca câmera por ID. SEMPRE exige city_id."""
        pass
    
    @abstractmethod
    def get_by_public_id(self, public_id: UUID, city_id: UUID):
        """Busca câmera por public_id. SEMPRE exige city_id."""
        pass
    
    @abstractmethod
    def list_by_city(self, city_id: UUID, is_active: Optional[bool] = None) -> List:
        """Lista câmeras de uma cidade. Filtra por is_active se fornecido."""
        pass
    
    @abstractmethod
    def exists(self, camera_id: UUID, city_id: UUID) -> bool:
        """Verifica se câmera existe na cidade."""
        pass
    
    @abstractmethod
    def count_by_city(self, city_id: UUID) -> int:
        """Conta câmeras de uma cidade."""
        pass
    
    @abstractmethod
    def update_recording_status(self, camera_id: UUID, city_id: UUID, enabled: bool) -> bool:
        """Atualiza status de gravação da câmera."""
        pass
