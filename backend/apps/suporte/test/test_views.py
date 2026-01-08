import pytest

from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
class TestSuporteViews:
    def test_chat_access_authenticated(self, api_client, viewer_user):
        """Garante que utilizadores autenticados conseguem aceder ao chat."""
        api_client.force_authenticate(user=viewer_user)
        url = reverse("support-chat-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_post_message_logic(self, api_client, viewer_user):
        """Valida a criação de uma mensagem e o retorno do autor."""
        api_client.force_authenticate(user=viewer_user)
        url = reverse("support-chat-list")
        data = {"conteudo": "Preciso de ajuda com a câmara 1"}
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        # Correção aplicada aqui: .email em vez de .emailt
        assert response.data["autor_email"] == viewer_user.email