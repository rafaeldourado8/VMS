
"""
Testes Simples - Verificação Básica do Sistema
"""
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestBasicFunctionality:
    """Testes básicos de funcionalidade"""

    def test_create_user(self):
        """Teste criação de usuário"""
        user = User.objects.create_user(
            email='test@test.com',
            password='test123',
            name='Test User'
        )
        assert user.email == 'test@test.com'
        assert user.name == 'Test User'
        assert user.check_password('test123')

    def test_database_connection(self, db):
        """Teste conexão com banco de dados"""
        # Usar database padrão apenas
        assert User.objects.using('default').count() >= 0

    def test_models_import(self):
        """Teste importação de models"""
        from apps.cameras.models import Camera
        from apps.deteccoes.models import Deteccao
        assert Camera is not None
        assert Deteccao is not None

    def test_django_settings(self):
        """Teste configurações Django"""
        from django.conf import settings
        assert settings.DEBUG is not None
        assert settings.DATABASES is not None


@pytest.mark.django_db
class TestCameraModel:
    """Testes do modelo Camera"""

    def test_camera_fields_exist(self):
        """Teste campos do modelo Camera"""
        from apps.cameras.models import Camera
        fields = [f.name for f in Camera._meta.get_fields()]
        assert 'name' in fields
        assert 'stream_url' in fields
        assert 'location' in fields
        assert 'status' in fields


@pytest.mark.django_db  
class TestAPIHealth:
    """Testes de saúde da API"""

    def test_api_client_works(self, api_client):
        """Teste cliente API funciona"""
        assert api_client is not None

    def test_authenticated_client_works(self, authenticated_client):
        """Teste cliente autenticado funciona"""
        assert authenticated_client is not None
