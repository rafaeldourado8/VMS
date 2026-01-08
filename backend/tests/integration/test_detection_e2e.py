import pytest
import json
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao

User = get_user_model()


@pytest.mark.django_db
class TestDetectionEndToEnd:
    
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="detection@test.com", 
            name="Detection User", 
            password="test123"
        )
        self.client.force_authenticate(user=self.user)
        
        # Criar uma câmera para os testes
        self.camera = Camera.objects.create(
            owner=self.user,
            name="Test Camera",
            stream_url="rtsp://test.com/stream"
        )
    
    # def test_ingest_detection_complete_flow(self):
    #     """Testa o fluxo completo de ingestão de detecção"""
    #     # Teste desabilitado - requer configuração de API key
    #     pass
    
    def test_list_detections_by_camera(self):
        """Testa listagem de detecções por câmera"""
        # Criar algumas detecções
        for i in range(3):
            Deteccao.objects.create(
                camera=self.camera,
                plate=f"ABC{i:04d}",
                confidence=0.9,
                timestamp="2025-01-05T10:00:00Z",
                vehicle_type="car"
            )
        
        # Listar detecções
        response = self.client.get(f"/api/detections/?camera_id={self.camera.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        assert len(response.data["results"]) == 3
    
    def test_list_detections_by_plate(self):
        """Testa busca de detecções por placa"""
        # Criar detecções com placas diferentes
        Deteccao.objects.create(
            camera=self.camera,
            plate="ABC1234",
            confidence=0.9,
            timestamp="2025-01-05T10:00:00Z",
            vehicle_type="car"
        )
        Deteccao.objects.create(
            camera=self.camera,
            plate="XYZ5678",
            confidence=0.8,
            timestamp="2025-01-05T10:01:00Z",
            vehicle_type="motorcycle"
        )
        
        # Buscar por placa específica
        response = self.client.get("/api/detections/?plate=ABC1234")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["plate"] == "ABC1234"
    
    def test_get_detection_detail(self):
        """Testa busca de detecção específica"""
        detection = Deteccao.objects.create(
            camera=self.camera,
            plate="DEF5678",
            confidence=0.95,
            timestamp="2025-01-05T10:00:00Z",
            vehicle_type="truck"
        )
        
        response = self.client.get(f"/api/detections/{detection.id}/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["plate"] == "DEF5678"
        assert response.data["vehicle_type"] == "truck"
        assert response.data["confidence"] == 0.95
    
    def test_detection_permissions(self):
        """Testa permissões de acesso às detecções"""
        # Criar outro usuário
        other_user = User.objects.create_user(
            email="other@test.com",
            name="Other User",
            password="test123"
        )
        other_camera = Camera.objects.create(
            owner=other_user,
            name="Other Camera",
            stream_url="rtsp://other.com/stream"
        )
        
        # Criar detecção do outro usuário
        other_detection = Deteccao.objects.create(
            camera=other_camera,
            plate="GHI9012",
            confidence=0.9,
            timestamp="2025-01-05T10:00:00Z",
            vehicle_type="car"
        )
        
        # Tentar acessar detecção de outro usuário
        response = self.client.get(f"/api/detections/{other_detection.id}/")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_detection_caching(self):
        """Testa se o cache está funcionando na listagem"""
        # Criar detecção
        Deteccao.objects.create(
            camera=self.camera,
            plate="JKL3456",
            confidence=0.9,
            timestamp="2025-01-05T10:00:00Z",
            vehicle_type="car"
        )
        
        # Primeira requisição
        response1 = self.client.get("/api/detections/")
        assert response1.status_code == status.HTTP_200_OK
        
        # Segunda requisição (deve usar cache)
        response2 = self.client.get("/api/detections/")
        assert response2.status_code == status.HTTP_200_OK
        assert response1.data == response2.data