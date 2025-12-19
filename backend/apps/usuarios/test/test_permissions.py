import pytest
from unittest.mock import Mock
from apps.usuarios.permissions import IsAdminOrReadOnly

class TestIsAdminOrReadOnly:
    def test_unsafe_methods_deny_viewer(self):
        """Garante que viewers não podem realizar POST/DELETE."""
        permission = IsAdminOrReadOnly()
        request = Mock(method="POST", user=Mock(is_authenticated=True, is_active=True, role="viewer"))
        assert permission.has_permission(request, Mock()) is False