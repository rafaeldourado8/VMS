import pytest
import time
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestCameraPerformance:
    
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="perf@test.com", 
            name="Perf User", 
            password="test123"
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_camera_performance(self):
        """Testa performance de criação de câmera"""
        data = {
            "name": "Perf Camera",
            "stream_url": "rtsp://perf.com/stream",
            "location": "Perf Location"
        }
        
        start_time = time.time()
        response = self.client.post("/api/cameras/", data)
        end_time = time.time()
        
        assert response.status_code == 201
        assert (end_time - start_time) < 1.0  # Deve ser menor que 1 segundo
    
    def test_list_cameras_performance(self):
        """Testa performance de listagem de câmeras"""
        # Criar algumas câmeras
        for i in range(5):
            self.client.post("/api/cameras/", {
                "name": f"Camera {i}",
                "stream_url": f"rtsp://cam{i}.com"
            })
        
        start_time = time.time()
        response = self.client.get("/api/cameras/")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Deve ser menor que 1 segundo
        assert response.data["count"] == 5
    
    def test_bulk_operations_performance(self):
        """Testa performance de operações em lote"""
        camera_ids = []
        
        # Criar 10 câmeras
        start_time = time.time()
        for i in range(10):
            response = self.client.post("/api/cameras/", {
                "name": f"Bulk Camera {i}",
                "stream_url": f"rtsp://bulk{i}.com"
            })
            camera_ids.append(response.data["id"])
        create_time = time.time() - start_time
        
        # Listar todas
        start_time = time.time()
        response = self.client.get("/api/cameras/")
        list_time = time.time() - start_time
        
        # Deletar todas
        start_time = time.time()
        for camera_id in camera_ids:
            self.client.delete(f"/api/cameras/{camera_id}/")
        delete_time = time.time() - start_time
        
        assert create_time < 5.0  # 10 criações em menos de 5s
        assert list_time < 1.0    # Listagem em menos de 1s
        assert delete_time < 3.0  # 10 deleções em menos de 3s
        assert response.data["count"] == 10