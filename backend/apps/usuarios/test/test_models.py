import pytest

from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUsuarioModel:
    def test_create_user_success(self):
        """Testa criação via manager."""
        user = User.objects.create_user(email="test@ex.com", name="Test", password="123")
        assert user.email == "test@ex.com"
        assert user.role == "viewer"

    def test_create_superuser_success(self):
        """Testa criação de administrador via manager."""
        user = User.objects.create_superuser(email="admin@ex.com", name="Admin", password="123")
        assert user.is_staff is True
        assert user.role == "admin"