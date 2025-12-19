import pytest
from django.contrib import admin
from apps.usuarios.models import Usuario
from apps.usuarios.admin import UsuarioAdmin

class TestUsuarioAdmin:
    def test_usuario_is_registered(self):
        """Verifica registo no admin."""
        registry = admin.site._registry
        assert Usuario in registry
        assert isinstance(registry[Usuario], UsuarioAdmin)