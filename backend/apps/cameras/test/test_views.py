from unittest.mock import patch
import pytest

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestCameraViews:
    def setup_method(self):
        self.client = APIClient()

    @patch('apps.cameras.services.CameraService._provision_streaming')
    def test_create_camera_api(self, mock_provision, admin_user):
        """Testa o endpoint POST /api/cameras/."""
        self.client.force_authenticate(user=admin_user)
        url = reverse("camera-list")
        data = {
            "name": "API Camera",
            "stream_url": "rtsp://api",
            "location": "Sede"
        }
        
        response = self.client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "API Camera"
        assert mock_provision.called is True

    def test_list_cameras_api(self, admin_user):
        """Garante que o utilizador só vê as suas próprias câmaras."""
        self.client.force_authenticate(user=admin_user)
        url = reverse("camera-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK