from ..queries.list_detections_query import ListDetectionsQuery
from typing import List

from domain.detection.entities.detection import Detection
from domain.detection.repositories.detection_repository import DetectionRepository
from domain.monitoring.repositories.camera_repository import CameraRepository

class ListDetectionsHandler:
    """Handler para listar detecções"""
    
    def __init__(
        self, 
        detection_repository: DetectionRepository,
        camera_repository: CameraRepository
    ):
        self.detection_repository = detection_repository
        self.camera_repository = camera_repository
    
    def handle(self, query: ListDetectionsQuery) -> List[Detection]:
        """Executa o use case de listar detecções"""
        
        if query.camera_id:
            camera = self.camera_repository.find_by_id(query.camera_id)
            if not camera or camera.owner_id != query.owner_id:
                return []
            
            return self.detection_repository.find_by_camera(
                query.camera_id, 
                query.limit
            )
        
        if query.plate:
            detections = self.detection_repository.find_by_plate(query.plate)
            user_cameras = self.camera_repository.find_by_owner(query.owner_id)
            camera_ids = {c.id for c in user_cameras}
            
            return [d for d in detections if d.camera_id in camera_ids]
        
        user_cameras = self.camera_repository.find_by_owner(query.owner_id)
        all_detections = []
        
        for camera in user_cameras:
            detections = self.detection_repository.find_by_camera(
                camera.id, 
                query.limit
            )
            all_detections.extend(detections)
        
        return all_detections[:query.limit]
