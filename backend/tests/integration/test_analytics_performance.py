import pytest
import time
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao
from datetime import datetime, timedelta

User = get_user_model()


@pytest.mark.django_db
class TestAnalyticsPerformance:
    
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="analytics@test.com", 
            name="Analytics User", 
            password="test123"
        )
        self.client.force_authenticate(user=self.user)
        
        # Criar dados de teste
        self.camera = Camera.objects.create(
            owner=self.user,
            name="Analytics Camera",
            stream_url="rtsp://analytics.com/stream",
            status="online"
        )
        
        # Criar detecções de teste
        base_time = datetime.now() - timedelta(hours=12)
        for i in range(100):
            Deteccao.objects.create(
                camera=self.camera,
                plate=f"TST{i:04d}",
                confidence=0.9,
                timestamp=base_time + timedelta(minutes=i*5),
                vehicle_type="car"
            )
    
    def test_dashboard_performance(self):
        """Testa performance do endpoint de dashboard"""
        
        start_time = time.time()
        response = self.client.get("/api/dashboard/stats/")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 2.0  # Deve ser menor que 2 segundos
        
        # Verificar estrutura da resposta
        data = response.data
        assert "total_detections" in data
        assert "active_cameras" in data
        assert "metrics" in data
        assert "summary" in data
    
    def test_dashboard_cache_performance(self):
        """Testa performance com cache"""
        
        # Primeira requisição (sem cache)
        start_time = time.time()
        response1 = self.client.get("/api/dashboard/stats/?period=day")
        first_request_time = time.time() - start_time
        
        assert response1.status_code == 200
        assert response1.data["cached"] is False
        
        # Segunda requisição (com cache)
        start_time = time.time()
        response2 = self.client.get("/api/dashboard/stats/?period=day")
        second_request_time = time.time() - start_time
        
        assert response2.status_code == 200
        assert response2.data["cached"] is True
        
        # Cache deve ser mais rápido
        assert second_request_time < first_request_time
        assert second_request_time < 0.1  # Cache deve ser muito rápido
    
    def test_different_periods_performance(self):
        """Testa performance com diferentes períodos"""
        
        periods = ['hour', 'day', 'week', 'month']
        
        for period in periods:
            start_time = time.time()
            response = self.client.get(f"/api/dashboard/stats/?period={period}")
            end_time = time.time()
            
            assert response.status_code == 200
            assert (end_time - start_time) < 2.0
            
            # Verificar que métricas foram calculadas
            assert len(response.data["metrics"]) > 0
    
    def test_large_dataset_performance(self):
        """Testa performance com dataset maior"""
        
        # Criar mais detecções
        base_time = datetime.now() - timedelta(days=7)
        for i in range(1000):  # 1000 detecções adicionais
            Deteccao.objects.create(
                camera=self.camera,
                plate=f"BIG{i:04d}",
                confidence=0.8,
                timestamp=base_time + timedelta(minutes=i*10),
                vehicle_type="motorcycle"
            )
        
        start_time = time.time()
        response = self.client.get("/api/dashboard/stats/?period=week")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 3.0  # Ainda deve ser rápido
        
        # Verificar que processou o dataset maior
        total_detections = response.data["total_detections"]
        assert int(total_detections) > 1000