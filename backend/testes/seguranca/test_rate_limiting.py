"""
Testes de Rate Limiting
"""
import pytest
from django.urls import reverse
from rest_framework import status
import time


@pytest.mark.django_db
class TestRateLimiting:
    """Testes de rate limiting"""

    def test_rate_limit_exceeded(self, authenticated_client):
        """Teste excesso de requisições"""
        url = reverse('camera-list')
        
        # Fazer múltiplas requisições rapidamente
        responses = []
        for i in range(150):  # Exceder limite de 100/min
            response = authenticated_client.get(url)
            responses.append(response.status_code)
        
        # Verificar se alguma requisição foi bloqueada
        assert status.HTTP_429_TOO_MANY_REQUESTS in responses

    def test_rate_limit_per_user(self, api_client, test_user, admin_user):
        """Teste rate limit por usuário"""
        from rest_framework_simplejwt.tokens import RefreshToken
        
        # Cliente 1
        refresh1 = RefreshToken.for_user(test_user)
        client1 = api_client
        client1.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh1.access_token}')
        
        # Cliente 2
        refresh2 = RefreshToken.for_user(admin_user)
        from rest_framework.test import APIClient
        client2 = APIClient()
        client2.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh2.access_token}')
        
        url = reverse('camera-list')
        
        # Cliente 1 excede limite
        for i in range(150):
            client1.get(url)
        
        # Cliente 2 ainda deve funcionar
        response = client2.get(url)
        assert response.status_code == status.HTTP_200_OK
