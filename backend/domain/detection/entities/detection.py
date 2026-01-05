from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..value_objects.license_plate import LicensePlate
from ..value_objects.confidence import Confidence
from ..value_objects.vehicle_type import VehicleType


@dataclass
class Detection:
    """Entidade de domínio Detection"""
    
    id: Optional[int]
    camera_id: int
    plate: LicensePlate
    confidence: Confidence
    timestamp: datetime
    vehicle_type: VehicleType = VehicleType.UNKNOWN
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Verifica se a detecção tem alta confiança"""
        return self.confidence.is_high(threshold)
    
    def has_plate(self) -> bool:
        """Verifica se a detecção possui placa"""
        return self.plate.value is not None
    
    def has_evidence(self) -> bool:
        """Verifica se possui evidências (imagem ou vídeo)"""
        return self.image_url is not None or self.video_url is not None
