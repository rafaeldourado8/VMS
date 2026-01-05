from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from ..entities.detection import Detection


class DetectionRepository(ABC):
    """Interface de repositório para Detection"""
    
    @abstractmethod
    def save(self, detection: Detection) -> Detection:
        """Salva uma detecção"""
        pass
    
    @abstractmethod
    def find_by_id(self, detection_id: int) -> Optional[Detection]:
        """Busca detecção por ID"""
        pass
    
    @abstractmethod
    def find_by_camera(self, camera_id: int, limit: int = 100) -> List[Detection]:
        """Busca detecções por câmera"""
        pass
    
    @abstractmethod
    def find_by_plate(self, plate: str) -> List[Detection]:
        """Busca detecções por placa"""
        pass
    
    @abstractmethod
    def find_by_period(self, start: datetime, end: datetime) -> List[Detection]:
        """Busca detecções por período"""
        pass
