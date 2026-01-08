import pytest

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status

@pytest.fixture(autouse=True)
def clear_cache_per_test():
    """Garante que o cache está limpo para cada teste individual."""
    cache.clear()
    yield
    cache.clear()

@pytest.mark.django_db
class TestDashboardViews:
    def test_dashboard_stats_unauthenticated(self, api_client):
        url = reverse("dashboard-stats")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_dashboard_stats_success(self, api_client, admin_user):
        """Valida a resposta do dashboard para utilizador autenticado."""
        api_client.force_authenticate(user=admin_user)
        url = reverse("dashboard-stats")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert "total_cameras" in response.data
        assert "cameras_status" in response.data
        assert "detections_24h" in response.data

    def test_dashboard_admin_global_cache(self, api_client, admin_user):
        """Testa se administradores recebem dados do cache global formatado."""
        api_client.force_authenticate(user=admin_user)
        admin_user.is_staff = True
        admin_user.save()
        
        # Mock de cache global com a estrutura correta
        cached_data = {
            "total_cameras": 500, 
            "cameras_status": {"online": 400, "offline": 100},
            "detections_24h": 1000,
            "cached": True
        }
        cache.set("global_dashboard_stats", cached_data)
        
        url = reverse("dashboard-stats")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_cameras"] == 500
        assert response.data["cached"] is True