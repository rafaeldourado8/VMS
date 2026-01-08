import pytest

from apps.cameras.models import Camera
from apps.cameras.schemas import CameraDTO

@pytest.mark.django_db
class TestCameraDTO:
    def test_dto_instantiation(self):
        """Testa se o DTO de câmara é instanciado corretamente."""
        dto = CameraDTO(
            name="Cam 1",
            stream_url="rtsp://test",
            owner_id=1,
            location="Entrada"
        )
        assert dto.name == "Cam 1"
        assert dto.status == "online"  # Valor padrão

    def test_from_model_method(self, db, admin_user):
        """Testa a conversão de Model Camera para DTO."""
        camera = Camera.objects.create(
            owner=admin_user,
            name="Camera Teste",
            stream_url="rtsp://camera1"
        )
        dto = CameraDTO.from_model(camera)
        
        assert dto.id == camera.id
        assert dto.owner_id == admin_user.id
        assert dto.name == "Camera Teste"
        assert dto.stream_url == "rtsp://camera1"