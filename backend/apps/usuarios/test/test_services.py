import pytest

from apps.usuarios.models import Usuario
from apps.usuarios.schemas import UsuarioDTO
from apps.usuarios.services import UsuarioService

@pytest.mark.django_db
class TestUsuarioService:
    def test_create_user_service(self):
        """Testa se o serviço cria o utilizador corretamente com hash de password."""
        dto = UsuarioDTO(email="service@test.com", name="Service User", role="viewer", password="secure_password")
        user = UsuarioService.create_user(dto)
        
        assert isinstance(user, Usuario)
        assert user.email == "service@test.com"
        assert user.check_password("secure_password") is True

    def test_list_users_service(self, db):
        """Testa a listagem de utilizadores via serviço."""
        Usuario.objects.create_user(email="u1@test.com", name="U1")
        Usuario.objects.create_user(email="u2@test.com", name="U2")
        
        users = UsuarioService.list_users()
        assert users.count() == 2