import pytest

from apps.cameras.models import Camera
from apps.cameras.serializers import CameraSerializer

@pytest.mark.django_db
class TestCameraSerializer:
    def test_serializer_computed_urls(self, db, admin_user):
        """Verifica se as URLs de WebRTC e IA são geradas corretamente."""
        camera = Camera.objects.create(owner=admin_user, name="URL Cam", stream_url="rtsp://url")
        serializer = CameraSerializer(camera)
        
        # O padrão deve seguir o roteamento do HAProxy
        assert serializer.data["stream_url_frontend"] == f"/ws/live/camera_{camera.id}"
        assert serializer.data["ai_websocket_url"] == f"/ai/stream/{camera.id}"
        assert "snapshot_url" in serializer.data

    def test_serializer_read_only_fields(self):
        """Garante que campos de metadados não são aceites no input."""
        data = {"name": "Test", "stream_url": "rtsp://test", "id": 999}
        serializer = CameraSerializer(data=data)
        serializer.is_valid()
        assert "id" not in serializer.validated_data