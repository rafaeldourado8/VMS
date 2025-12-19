import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.conf import settings

User = get_user_model()

@pytest.fixture(autouse=True)
def use_dummy_cache(settings):
    """
    Substitui o Redis por cache em memória durante os testes para evitar 
    erros de conexão e garantir o isolamento total da suíte.
    """
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

@pytest.fixture
def test_password():
    return "pass123"

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db, test_password):
    """Fixture global de administrador."""
    return User.objects.create_superuser(
        email="admin@test.com", 
        name="Admin", 
        password=test_password
    )

@pytest.fixture
def viewer_user(db, test_password):
    """Fixture global de visualizador."""
    return User.objects.create_user(
        email="viewer@test.com", 
        name="Viewer", 
        password=test_password, 
        role="viewer"
    )