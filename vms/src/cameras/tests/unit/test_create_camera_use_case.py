import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from application.use_cases.create_camera import CreateCameraUseCase, CreateCameraRequest
from domain.entities.camera import Camera

class InMemoryCameraRepository:
    def __init__(self):
        self.cameras = {}
    
    def save(self, camera: Camera) -> None:
        self.cameras[camera.id] = camera
    
    def find_by_id(self, camera_id: str) -> Camera | None:
        return self.cameras.get(camera_id)
    
    def list_by_city(self, city_id: str) -> list[Camera]:
        return [c for c in self.cameras.values() if c.city_id == city_id]
    
    def count_by_city(self, city_id: str) -> int:
        return len([c for c in self.cameras.values() if c.city_id == city_id])
    
    def count_lpr_by_city(self, city_id: str) -> int:
        return len([c for c in self.cameras.values() if c.city_id == city_id and c.lpr_enabled])
    
    def delete(self, camera_id: str) -> None:
        self.cameras.pop(camera_id, None)

def test_create_camera_rtsp_success():
    repo = InMemoryCameraRepository()
    use_case = CreateCameraUseCase(repo)
    
    request = CreateCameraRequest(
        name='Camera LPR 1',
        stream_url='rtsp://example.com/stream',
        city_id='city-1'
    )
    
    camera_id = use_case.execute(request)
    
    assert camera_id is not None
    camera = repo.find_by_id(camera_id)
    assert camera.name == 'Camera LPR 1'
    assert camera.type == 'rtsp'
    assert camera.lpr_enabled is True

def test_create_camera_rtmp_success():
    repo = InMemoryCameraRepository()
    use_case = CreateCameraUseCase(repo)
    
    request = CreateCameraRequest(
        name='Camera Bullet 1',
        stream_url='rtmp://example.com/stream',
        city_id='city-1'
    )
    
    camera_id = use_case.execute(request)
    camera = repo.find_by_id(camera_id)
    
    assert camera.type == 'rtmp'
    assert camera.lpr_enabled is False

def test_create_camera_max_limit():
    repo = InMemoryCameraRepository()
    
    # Adiciona 1000 câmeras
    for i in range(1000):
        camera = Camera(id=str(i), name=f'Cam {i}', stream_url='rtmp://url', city_id='city-1')
        repo.save(camera)
    
    use_case = CreateCameraUseCase(repo)
    request = CreateCameraRequest(name='Cam', stream_url='rtmp://url', city_id='city-1')
    
    with pytest.raises(ValueError, match="Maximum cameras limit"):
        use_case.execute(request)

def test_create_camera_max_lpr_limit():
    repo = InMemoryCameraRepository()
    
    # Adiciona 20 câmeras LPR (RTSP)
    for i in range(20):
        camera = Camera(id=str(i), name=f'Cam {i}', stream_url='rtsp://url', city_id='city-1')
        repo.save(camera)
    
    use_case = CreateCameraUseCase(repo)
    request = CreateCameraRequest(name='Cam', stream_url='rtsp://url', city_id='city-1')
    
    with pytest.raises(ValueError, match="Maximum LPR cameras limit"):
        use_case.execute(request)
