from domain.monitoring.entities.camera import Camera
from domain.monitoring.repositories.camera_repository import CameraRepository


class GetCameraQuery:
    def __init__(self, camera_id: int, owner_id: int):
        self.camera_id = camera_id
        self.owner_id = owner_id


class GetCameraHandler:
    def __init__(self, repository: CameraRepository):
        self.repository = repository
    
    def handle(self, query: GetCameraQuery) -> Camera:
        camera = self.repository.find_by_id(query.camera_id)
        if not camera or camera.owner_id != query.owner_id:
            raise ValueError("Câmera não encontrada")
        return camera
