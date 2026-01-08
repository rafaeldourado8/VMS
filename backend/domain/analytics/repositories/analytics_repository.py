from ..entities.metric import Metric
from ..value_objects.period import Period
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AnalyticsRepository(ABC):
    """Interface de repositório para Analytics"""
    
    @abstractmethod
    def get_detection_count(self, period: Period, camera_id: int = None) -> int:
        """Conta detecções no período"""
        pass
    
    @abstractmethod
    def get_active_cameras_count(self) -> int:
        """Conta câmeras ativas"""
        pass
    
    @abstractmethod
    def get_detections_by_camera(self, period: Period) -> Dict[int, int]:
        """Detecções agrupadas por câmera"""
        pass
    
    @abstractmethod
    def get_detections_by_hour(self, period: Period) -> Dict[int, int]:
        """Detecções agrupadas por hora"""
        pass