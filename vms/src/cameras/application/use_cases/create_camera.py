from dataclasses import dataclass
from uuid import uuid4
from domain.entities.camera import Camera
from domain.repositories.camera_repository import ICameraRepository

@dataclass
class CreateCameraRequest:
    name: str
    stream_url: str
    city_id: str

class CreateCameraUseCase:
    def __init__(self, repo: ICameraRepository):
        self._repo = repo
    
    def execute(self, request: CreateCameraRequest) -> str:
        # Cria câmera (tipo é auto-detectado pela URL)
        camera = Camera(
            id=str(uuid4()),
            name=request.name,
            stream_url=request.stream_url,
            city_id=request.city_id
        )
        
        # Validar limites
        current_count = self._repo.count_by_city(request.city_id)
        if current_count >= 1000:
            raise ValueError("Maximum cameras limit reached (1000)")
        
        if camera.is_lpr_enabled():
            lpr_count = self._repo.count_lpr_by_city(request.city_id)
            if lpr_count >= 20:
                raise ValueError("Maximum LPR cameras limit reached (20)")
        
        self._repo.save(camera)
        return camera.id
