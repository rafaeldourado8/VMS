import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestCameraViewSet:
    
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@test.com", 
            name="Test User", 
            password="test123"
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_camera(self):
        data = {
            "name": "Test Camera",
            "stream_url": "rtsp://test.com/stream",
            "location": "Test Location"
        }
        
        response = self.client.post("/api/cameras/", data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Test Camera"
        assert response.data["stream_url"] == "rtsp://test.com/stream"
    
    def test_list_cameras(self):
        # Criar uma câmera primeiro
        self.client.post("/api/cameras/", {
            "name": "Camera 1",
            "stream_url": "rtsp://cam1.com"
        })
        
        response = self.client.get("/api/cameras/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Camera 1"
    
    def test_get_camera(self):
        # Criar câmera
        create_response = self.client.post("/api/cameras/", {
            "name": "Get Test",
            "stream_url": "rtsp://get.com"
        })
        camera_id = create_response.data["id"]
        
        response = self.client.get(f"/api/cameras/{camera_id}/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Get Test"
    
    def test_update_camera(self):
        # Criar câmera
        create_response = self.client.post("/api/cameras/", {
            "name": "Update Test",
            "stream_url": "rtsp://update.com"
        })
        camera_id = create_response.data["id"]
        
        # Atualizar
        response = self.client.patch(f"/api/cameras/{camera_id}/", {
            "name": "Updated Name"
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Name"
    
    def test_delete_camera(self):
        # Criar câmera
        create_response = self.client.post("/api/cameras/", {
            "name": "Delete Test",
            "stream_url": "rtsp://delete.com"
        })
        camera_id = create_response.data["id"]
        
        # Deletar
        response = self.client.delete(f"/api/cameras/{camera_id}/")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verificar se foi deletada
        get_response = self.client.get(f"/api/cameras/{camera_id}/")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND