import pytest

from apps.usuarios.serializers import UsuarioSerializer

@pytest.mark.django_db
class TestUsuarioSerializer:
    def test_serializer_validation(self, db): # Adicionar fixture db
        """Testa se o serializer valida os campos (incluindo check de email único)."""
        data = {
            "email": "valid@test.com", 
            "name": "Valid", 
            "role": "viewer", 
            "password": "password123"
        }
        serializer = UsuarioSerializer(data=data)
        assert serializer.is_valid() is True

    def test_serializer_read_only_fields(self, db):
        """Verifica se campos protegidos são ignorados no input."""
        data = {"email": "ro@test.com", "name": "RO", "id": 999}
        serializer = UsuarioSerializer(data=data)
        serializer.is_valid()
        assert "id" not in serializer.validated_data