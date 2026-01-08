from unittest.mock import patch
import pytest

from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestThumbnailViews:
    @patch('apps.thumbnails.services.ThumbnailService.get_snapshot')
    def test_snapshot_view_returns_image(self, mock_get_snapshot, api_client, admin_user):
        """Valida se a view retorna o Content-Type correto."""
        api_client.force_authenticate(user=admin_user)
        mock_get_snapshot.return_value = b'fake_image_bytes'
        
        # URL definida em apps/thumbnails/urls.py
        url = reverse("camera-snapshot", kwargs={"camera_id": 1})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == "image/jpeg"