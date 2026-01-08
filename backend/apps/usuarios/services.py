from .models import Usuario
from .schemas import UsuarioDTO

from django.db import transaction

class UsuarioService:
    """Camada de serviço para gestão de utilizadores."""

    @staticmethod
    def create_user(data: UsuarioDTO) -> Usuario:
        """Cria um utilizador no sistema com hashing de password."""
        with transaction.atomic():
            user = Usuario.objects.create_user(
                email=data.email,
                name=data.name,
                password=data.password,
                role=data.role,
                is_active=data.is_active
            )
        return user

    @staticmethod
    def list_users():
        """Retorna todos os utilizadores ordenados por data de criação."""
        return Usuario.objects.all().order_by("-created_at")