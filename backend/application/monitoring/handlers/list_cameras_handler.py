from typing import List
from domain.monitoring.entities.camera import Camera
from domain.monitoring.repositories.camera_repository import CameraRepository
from ..queries.list_cameras_query import ListCamerasQuery


class ListCamerasHandler:
    """Handler para listar câmeras"""
    
    def __init__(self, repository: CameraRepository):
        self.repository = repository
    
    def handle(self, query: ListCamerasQuery) -> List[Camera]:
        """Executa o use case de listar câmeras"""
        return self.repository.find_by_owner(query.owner_id)
