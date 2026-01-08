import pytest

from django.utils import timezone

from apps.deteccoes.models import Deteccao
from apps.deteccoes.schemas import IngestDeteccaoDTO
from apps.deteccoes.services import DeteccaoService

@pytest.mark.django_db
class TestDeteccaoService:
    def test_process_ingestion_success(self, db, admin_user):
        """Testa se o serviço salva a detecção corretamente."""
        # Criar uma câmara para o teste
        from apps.cameras.models import Camera
        camera = Camera.objects.create(owner=admin_user, name="Cam Test", stream_url="rtsp://test")
        
        dto = IngestDeteccaoDTO(
            camera_id=camera.id,
            timestamp=timezone.now(),
            plate="ABC1234",
            confidence=0.98,
            vehicle_type="car"
        )
        
        deteccao = DeteccaoService.process_ingestion(dto)
        assert deteccao.plate == "ABC1234"
        assert Deteccao.objects.count() == 1

    def test_process_ingestion_invalid_camera(self, db):
        """Garante que falha ao tentar ingerir para uma câmara que não existe."""
        dto = IngestDeteccaoDTO(camera_id=999, timestamp=timezone.now())
        with pytest.raises(ValueError) as excinfo:
            DeteccaoService.process_ingestion(dto)
        assert "inexistente" in str(excinfo.value)