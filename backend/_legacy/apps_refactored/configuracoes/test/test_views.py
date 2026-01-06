import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestConfiguracoesViews:
    def test_admin_update_success(self, api_client, admin_user):
        """Garante que o administrador consegue atualizar via PATCH enviando JSON."""
        api_client.force_authenticate(user=admin_user)
        url = reverse("global-settings")
        
        # Enviamos explicitamente como JSON para evitar ambiguidades de string
        response = api_client.patch(url, {"em_manutencao": True}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        # Agora o valor retornado será True (bool) e não 'True' (str)
        assert response.data["em_manutencao"] is True

    def test_unauthorized_access(self, api_client, viewer_user):
        """Garante que utilizadores sem role de admin são bloqueados."""
        api_client.force_authenticate(user=viewer_user)
        url = reverse("global-settings")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN