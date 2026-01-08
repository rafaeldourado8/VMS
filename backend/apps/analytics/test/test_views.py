import pytest

from django.core.cache import cache
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestAnalyticsViews:
    def test_vehicle_types_endpoint_and_cache(self, api_client, admin_user):
        """Testa o endpoint de tipos e se os dados são cacheados."""
        api_client.force_authenticate(user=admin_user)
        url = reverse("vehicle-types")
        
        # Primeiro pedido (Cache MISS)
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Verificar se a chave foi criada no cache
        cache_key = f"analytics_types_{admin_user.id}"
        assert cache.get(cache_key) is not None

    def test_detections_by_period_params(self, api_client, admin_user):
        """Valida o endpoint de período com parâmetros de query."""
        api_client.force_authenticate(user=admin_user)
        url = reverse("detections-by-period")
        
        # Testar com período específico
        response = api_client.get(url, {"period": "hour"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["period"] == "hour"