from domain.entities.camera import Camera
from domain.repositories.camera_repository import ICameraRepository

class ListCamerasUseCase:
    def __init__(self, repo: ICameraRepository):
        self._repo = repo
    
    def execute(self, city_id: str) -> list[Camera]:
        return self._repo.list_by_city(city_id)
