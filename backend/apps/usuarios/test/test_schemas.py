import pytest

from apps.usuarios.models import Usuario
from apps.usuarios.schemas import UsuarioDTO

@pytest.mark.django_db
class TestUsuarioDTO:
    def test_dto_instantiation(self):
        """Testa se o DTO é instanciado corretamente."""
        dto = UsuarioDTO(email="dto@test.com", name="DTO Test", role="viewer", password="123")
        assert dto.email == "dto@test.com"
        assert dto.password == "123"

    def test_from_model_method(self, db):
        """Testa a conversão de Model para DTO."""
        user = Usuario.objects.create_user(email="model@test.com", name="Model User", role="admin")
        dto = UsuarioDTO.from_model(user)
        
        assert dto.id == user.id
        assert dto.email == user.email
        assert dto.name == user.name
        assert dto.role == "admin"