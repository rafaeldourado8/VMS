import pytest

from django.conf import settings
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestDeteccaoViews:
    def test_ingest_without_api_key_fails(self, api_client):
        """Garante que o acesso é negado sem a chave X-API-Key."""
        url = reverse("ingest-deteccao")
        response = api_client.post(url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_ingest_with_valid_api_key(self, api_client, admin_user):
        """Testa a ingestão bem-sucedida com API Key configurada."""
        from apps.cameras.models import Camera
        camera = Camera.objects.create(owner=admin_user, name="Ingest Cam", stream_url="rtsp://ingest")
        
        # Simula a chave vinda do .env/settings
        settings.INGEST_API_KEY = "super-secret-key"
        url = reverse("ingest-deteccao")
        
        data = {
            "camera_id": camera.id,
            "timestamp": "2025-10-16T14:59:47Z",
            "plate": "XYZ7890",
            "vehicle_type": "truck"
        }
        
        response = api_client.post(url, data, HTTP_X_API_KEY="super-secret-key")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["plate"] == "XYZ7890"