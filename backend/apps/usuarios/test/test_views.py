import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient # Importar APIClient

User = get_user_model()

@pytest.fixture
def test_password():
    return "pass123"

@pytest.fixture
def api_client():
    """Fixture que retorna o cliente de teste do DRF."""
    return APIClient()

@pytest.fixture
def admin_user(db, test_password):
    """Sobrescreve a fixture padrão para incluir o campo 'name' obrigatório."""
    return User.objects.create_superuser(
        email="admin@test.com", name="Admin", password=test_password
    )

@pytest.fixture
def viewer_user(db, test_password):
    return User.objects.create_user(
        email="viewer@test.com", name="Viewer", password=test_password, role="viewer"
    )

@pytest.fixture
def auth_client(api_client, admin_user, test_password):
    """Retorna APIClient autenticado como admin."""
    resp = api_client.post(reverse("token_obtain_pair"), {
        "email": admin_user.email,
        "password": test_password
    })
    token = resp.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client

@pytest.mark.django_db
class TestUsuarioViews:
    
    def test_create_user_integration(self, auth_client):
        url = reverse("usuario-list")
        data = {
            "email": "api@test.com", 
            "name": "API User", 
            "role": "viewer", 
            "password": "password123"
        }
        response = auth_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "api@test.com"

    def test_me_endpoint(self, api_client, viewer_user, test_password):
        # Autenticar viewer manualmente
        resp = api_client.post(reverse("token_obtain_pair"), {
            "email": viewer_user.email,
            "password": test_password
        })
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
        
        url = reverse("auth_me")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == viewer_user.email