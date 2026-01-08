from ..commands.process_detection_command import ProcessDetectionCommand

from domain.detection.entities.detection import Detection
from domain.detection.repositories.detection_repository import DetectionRepository
from domain.detection.value_objects.confidence import Confidence
from domain.detection.value_objects.license_plate import LicensePlate
from domain.detection.value_objects.vehicle_type import VehicleType

class ProcessDetectionHandler:
    """Handler para processar detecção"""
    
    def __init__(self, repository: DetectionRepository):
        self.repository = repository
    
    def handle(self, command: ProcessDetectionCommand) -> Detection:
        """Executa o use case de processar detecção"""
        
        detection = Detection(
            id=None,
            camera_id=command.camera_id,
            plate=LicensePlate(command.plate),
            confidence=Confidence(command.confidence),
            timestamp=command.timestamp,
            vehicle_type=VehicleType(command.vehicle_type),
            image_url=command.image_url,
            video_url=command.video_url
        )
        
        return self.repository.save(detection)
