from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from shared.streaming.recording.models import RecordingSession

class RecordingManager(ABC):
    @abstractmethod
    def enable_recording(self, camera_id: UUID, city_id: UUID) -> RecordingSession:
        """Habilita gravação para uma câmera"""
        pass
    
    @abstractmethod
    def disable_recording(self, camera_id: UUID, city_id: UUID) -> bool:
        """Desabilita gravação para uma câmera"""
        pass
    
    @abstractmethod
    def get_status(self, camera_id: UUID, city_id: UUID) -> Optional[RecordingSession]:
        """Retorna status da gravação"""
        pass
