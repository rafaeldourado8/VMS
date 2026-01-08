from unittest.mock import Mock
import pytest

from apps.cameras.permissions import IsAdminOrReadOnly

class TestCameraPermissions:
    def test_viewer_can_read_but_not_write(self):
        """Valida que um viewer pode ler (GET) mas não criar (POST)."""
        permission = IsAdminOrReadOnly()
        
        # Mock de request GET
        get_request = Mock(method="GET", user=Mock(is_authenticated=True))
        assert permission.has_permission(get_request, Mock()) is True
        
        # Mock de request POST para Viewer
        post_request = Mock(method="POST", user=Mock(is_authenticated=True, is_active=True, role="viewer"))
        assert permission.has_permission(post_request, Mock()) is False