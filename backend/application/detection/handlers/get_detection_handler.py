from domain.detection.entities.detection import Detection
from domain.detection.repositories.detection_repository import DetectionRepository
from domain.monitoring.repositories.camera_repository import CameraRepository


class GetDetectionQuery:
    def __init__(self, detection_id: int, owner_id: int):
        self.detection_id = detection_id
        self.owner_id = owner_id


class GetDetectionHandler:
    def __init__(
        self, 
        detection_repository: DetectionRepository,
        camera_repository: CameraRepository
    ):
        self.detection_repository = detection_repository
        self.camera_repository = camera_repository
    
    def handle(self, query: GetDetectionQuery) -> Detection:
        detection = self.detection_repository.find_by_id(query.detection_id)
        if not detection:
            raise ValueError("Detecção não encontrada")
        
        camera = self.camera_repository.find_by_id(detection.camera_id)
        if not camera or camera.owner_id != query.owner_id:
            raise ValueError("Detecção não encontrada")
        
        return detection
