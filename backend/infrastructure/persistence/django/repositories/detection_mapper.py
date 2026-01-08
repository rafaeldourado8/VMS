from typing import Optional

from apps.deteccoes.models import Deteccao as DetectionModel
from domain.detection.entities.detection import Detection
from domain.detection.value_objects.confidence import Confidence
from domain.detection.value_objects.license_plate import LicensePlate
from domain.detection.value_objects.vehicle_type import VehicleType

class DetectionMapper:
    """Mapper entre entidade Detection e DetectionModel Django"""
    
    @staticmethod
    def to_domain(model: DetectionModel) -> Detection:
        """Converte DetectionModel para entidade Detection"""
        return Detection(
            id=model.id,
            camera_id=model.camera_id,
            plate=LicensePlate(model.plate),
            confidence=Confidence(model.confidence),
            timestamp=model.timestamp,
            vehicle_type=VehicleType(model.vehicle_type),
            image_url=model.image_url,
            video_url=model.video_url,
            created_at=model.created_at
        )
    
    @staticmethod
    def to_model(detection: Detection, model: Optional[DetectionModel] = None) -> DetectionModel:
        """Converte entidade Detection para DetectionModel"""
        if model is None:
            model = DetectionModel()
        
        model.camera_id = detection.camera_id
        model.plate = str(detection.plate)
        model.confidence = float(detection.confidence)
        model.timestamp = detection.timestamp
        model.vehicle_type = detection.vehicle_type.value
        model.image_url = detection.image_url
        model.video_url = detection.video_url
        
        return model
