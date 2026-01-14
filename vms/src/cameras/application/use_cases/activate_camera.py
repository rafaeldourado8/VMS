from domain.repositories.camera_repository import ICameraRepository

class ActivateCameraUseCase:
    def __init__(self, repo: ICameraRepository):
        self._repo = repo
    
    def execute(self, camera_id: str) -> None:
        camera = self._repo.find_by_id(camera_id)
        if not camera:
            raise ValueError(f"Camera {camera_id} not found")
        
        camera.activate()
        self._repo.save(camera)
