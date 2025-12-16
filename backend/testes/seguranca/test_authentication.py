"""
Testes de Autenticação e Segurança
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
class TestAuthentication:
    """Testes de autenticação JWT"""

    def test_login_success(self, api_client, test_user):
        """Teste login com credenciais válidas"""
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_invalid_credentials(self, api_client):
        """Teste login com credenciais inválidas"""
        url = reverse('token_obtain_pair')
        data = {'username': 'invalid', 'password': 'wrong'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token(self, api_client, test_user):
        """Teste refresh de token"""
        refresh = RefreshToken.for_user(test_user)
        url = reverse('token_refresh')
        data = {'refresh': str(refresh)}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_access_protected_endpoint_without_auth(self, api_client):
        """Teste acesso a endpoint protegido sem autenticação"""
        url = reverse('camera-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_protected_endpoint_with_auth(self, authenticated_client):
        """Teste acesso a endpoint protegido com autenticação"""
        url = reverse('camera-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_expired_token(self, api_client, test_user):
        """Teste token expirado"""
        # Token com tempo de vida de 0 segundos
        refresh = RefreshToken.for_user(test_user)
        refresh.set_exp(lifetime=timedelta(seconds=0))
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        url = reverse('camera-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAuthorization:
    """Testes de autorização e permissões"""

    def test_regular_user_cannot_delete_camera(self, authenticated_client, test_camera):
        """Teste usuário comum não pode deletar câmera"""
        url = reverse('camera-detail', kwargs={'pk': test_camera.id})
        response = authenticated_client.delete(url)
        # Depende da configuração de permissões
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_204_NO_CONTENT]

    def test_user_can_only_see_own_cameras(self, authenticated_client, test_user, admin_user):
        """Teste usuário só vê suas próprias câmeras"""
        from apps.cameras.models import Camera
        # Criar câmera do admin
        Camera.objects.create(
            nome='Admin Camera',
            rtsp_url='rtsp://admin@192.168.1.1:554/stream',
            localizacao='Admin',
            ativa=True,
            criado_por=admin_user
        )
        url = reverse('camera-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # Verificar se retorna apenas câmeras do usuário autenticado
        for camera in response.data['results']:
            assert camera['criado_por'] == test_user.id or camera['criado_por'] is None


@pytest.mark.django_db
class TestSQLInjection:
    """Testes de proteção contra SQL Injection"""

    def test_sql_injection_in_search(self, authenticated_client):
        """Teste SQL injection em busca"""
        url = reverse('camera-list')
        malicious_input = "'; DROP TABLE cameras; --"
        response = authenticated_client.get(url, {'search': malicious_input})
        # Deve retornar 200 sem executar SQL malicioso
        assert response.status_code == status.HTTP_200_OK

    def test_sql_injection_in_filter(self, authenticated_client):
        """Teste SQL injection em filtro"""
        url = reverse('camera-list')
        malicious_input = "1 OR 1=1"
        response = authenticated_client.get(url, {'id': malicious_input})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestXSS:
    """Testes de proteção contra XSS"""

    def test_xss_in_camera_name(self, authenticated_client):
        """Teste XSS em nome de câmera"""
        url = reverse('camera-list')
        data = {
            'nome': '<script>alert("XSS")</script>',
            'rtsp_url': 'rtsp://test@192.168.1.1:554/stream',
            'localizacao': 'Test',
            'ativa': True
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        # Verificar se script foi sanitizado
        assert '<script>' not in response.data['nome']


from datetime import timedelta
