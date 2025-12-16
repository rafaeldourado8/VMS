"""
Configuração global de fixtures para pytest
"""
import pytest
import os
import django
from django.conf import settings
from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.cameras.models import Camera

User = get_user_model()


@pytest.fixture(scope='session')
def django_db_setup():
    """Setup do banco de dados para testes"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }


@pytest.fixture
def api_client():
    """Cliente API REST"""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Cliente autenticado com JWT"""
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def test_user(db):
    """Usuário de teste"""
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        name='Test User'
    )


@pytest.fixture
def admin_user(db):
    """Usuário admin"""
    return User.objects.create_superuser(
        email='admin@example.com',
        password='admin123',
        name='Admin User'
    )


@pytest.fixture
def test_camera(db, test_user):
    """Câmera de teste"""
    return Camera.objects.create(
        nome='Camera Teste',
        rtsp_url='rtsp://test:test@192.168.1.100:554/stream1',
        localizacao='Teste',
        ativa=True,
        criado_por=test_user
    )


@pytest.fixture
def multiple_cameras(db, test_user):
    """Múltiplas câmeras para testes de carga"""
    cameras = []
    for i in range(10):
        cameras.append(Camera.objects.create(
            nome=f'Camera {i}',
            rtsp_url=f'rtsp://test:test@192.168.1.{100+i}:554/stream1',
            localizacao=f'Local {i}',
            ativa=True,
            criado_por=test_user
        ))
    return cameras
