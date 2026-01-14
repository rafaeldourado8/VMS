import pytest
from fastapi.testclient import TestClient
from main import app
from admin.presentation.fastapi.container import container
from admin.tests.conftest import InMemoryUserRepository


@pytest.fixture
def client():
    # Usa repositório em memória para testes
    container._instances["user_repo"] = InMemoryUserRepository()
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    # Cria usuário
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "senha123",
        "city_ids": ["sao-paulo"]
    })
    
    # Login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "senha123"
    })
    
    return response.json()["token"]
