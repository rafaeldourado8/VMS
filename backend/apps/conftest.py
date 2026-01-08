import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture(autouse=True)
def use_dummy_cache(settings):
    """
    Substitui o Redis por cache em memória durante os testes.
    Isto evita erros de conexão (Error 10061) nos módulos de:
    - Thumbnails (geração de snapshots)
    - Dashboard (estatísticas globais)
    - Analytics (agregação de dados)
    - Detecções (listagem cacheada)
    """
    settings.CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

@pytest.fixture(autouse=True)
def setup_ingest_settings(settings):
    """
    Configura variáveis de ambiente críticas para testes de integração.
    Garante que a HasIngestAPIKey funcione nos testes de detecções.
    """
    settings.INGEST_API_KEY = "test-ingest-key-123"

@pytest.fixture
def api_client():
    """Fixture para realizar chamadas à API REST."""
    return APIClient()

@pytest.fixture
def test_password():
    """Palavra-passe padrão para utilizadores de teste."""
    return "pass123"

@pytest.fixture
def admin_user(db, test_password):
    """
    Fixture de administrador.
    Utilizado para testar permissões de gestão de câmaras e visualização 
    de todas as mensagens de suporte.
    """
    return User.objects.create_superuser(
        email="admin@test.com", 
        name="Admin", 
        password=test_password
    )

@pytest.fixture
def viewer_user(db, test_password):
    """
    Fixture de visualizador comum.
    Utilizado para garantir o isolamento de dados (ex: um viewer só vê 
    as suas próprias câmaras e mensagens).
    """
    return User.objects.create_user(
        email="viewer@test.com", 
        name="Viewer", 
        password=test_password, 
        role="viewer"
    )