import pytest
from unittest.mock import patch, MagicMock
from apps.thumbnails.services import ThumbnailService
from apps.cameras.models import Camera

@pytest.mark.django_db
class TestThumbnailService:
    @patch('subprocess.Popen')
    def test_get_snapshot_success(self, mock_popen, admin_user):
        """Simula a geração de um snapshot com sucesso via FFmpeg."""
        # Setup: Criar câmara de teste
        cam = Camera.objects.create(
            owner=admin_user, 
            name="Thumb Cam", 
            stream_url="rtsp://test-url"
        )
        
        # Simular o comportamento do processo FFmpeg
        mock_process = MagicMock()
        mock_process.communicate.return_value = (b'fake_jpeg_binary_data', b'')
        mock_process.returncode = 0
        mock_popen.return_value = mock_process

        service = ThumbnailService()
        result = service.get_snapshot(cam.id)

        assert result == b'fake_jpeg_binary_data'
        assert mock_popen.called

    def test_get_snapshot_camera_not_found(self):
        """Garante retorno None se a câmara não existir."""
        service = ThumbnailService()
        assert service.get_snapshot(9999) is None