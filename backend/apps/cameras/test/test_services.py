from httpx import Response
import pytest
import respx

from apps.cameras.models import Camera
from apps.cameras.schemas import CameraDTO
from apps.cameras.services import CameraService

@pytest.mark.django_db
class TestCameraService:
    @respx.mock
    def test_create_camera_service(self, admin_user):
        """Testa a criação de câmara e a notificação ao serviço de streaming."""
        service = CameraService()
        
        # Mock do serviço de streaming
        route = respx.post(f"{service.streaming_url}/cameras/provision").mock(
            return_value=Response(201, json={"status": "provisioned"})
        )
        
        dto = CameraDTO(
            name="Service Cam",
            stream_url="rtsp://service",
            owner_id=admin_user.id
        )
        
        camera = service.create_camera(dto)
        
        assert isinstance(camera, Camera)
        assert Camera.objects.count() == 1
        assert route.called is True

    @respx.mock
    def test_delete_camera_service(self, db, admin_user):
        """Testa a remoção da câmara e a chamada de limpeza no streaming."""
        camera = Camera.objects.create(owner=admin_user, name="Del Cam", stream_url="rtsp://del")
        service = CameraService()
        
        route = respx.delete(f"{service.streaming_url}/cameras/{camera.id}").mock(
            return_value=Response(200)
        )
        
        service.delete_camera(camera.id)
        
        assert Camera.objects.count() == 0
        assert route.called is True