# apps/usuarios/tests.py

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Obtém o modelo de usuário que criamos (Usuario)
User = get_user_model()


class UsuarioAuthTest(APITestCase):
    """Testes para login e criação de usuários (Endpoints 1.1 e 7.2)"""

    # Senhas fortes para garantir que o Django não as rejeite antes do teste de permissão
    ADMIN_PASSWORD = "AdminPassword123!"
    VIEWER_PASSWORD = "ViewerPassword123!"

    def setUp(self):
        # 1. Cria um usuário admin para os testes
        self.admin_user = User.objects.create_superuser(
            email="admin_teste@gt.com", name="Test Admin", password=self.ADMIN_PASSWORD
        )
        # 2. Define o payload (corpo do POST) para o login
        self.login_payload = {
            "email": "admin_teste@gt.com",
            "password": self.ADMIN_PASSWORD,
        }
        self.login_url = reverse("token_obtain_pair")
        self.list_url = reverse("usuario-list")  # Rota /api/users/

    def test_login_success(self):
        """Testa se o login (POST /api/auth/login/) retorna tokens"""
        response = self.client.post(self.login_url, self.login_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_admin_can_create_user(self):
        """Testa se um admin (logado) pode criar um novo usuário comum"""

        # 1. Faz login para obter o token de admin
        login_response = self.client.post(
            self.login_url, self.login_payload, format="json"
        )
        admin_token = login_response.data["access"]

        # 2. Define o novo usuário a ser criado
        new_user_payload = {
            "email": "novo@viewer.com",
            "name": "New Viewer",
            "password": "viewerpassword",
            "role": "viewer",
        }

        # 3. Faz o POST para criar o usuário (usando o token na header)
        response = self.client.post(
            self.list_url,
            new_user_payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {admin_token}",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            User.objects.count(), 2
        )  # Confirma que 2 usuários existem (admin + novo)

    def test_viewer_cannot_create_user(self):
        """Testa se um usuário comum NÃO pode criar outro usuário"""

        # 1. Cria um usuário comum (role padrão é 'viewer')
        viewer_user = User.objects.create_user(
            email="viewer@gt.com",
            name="Viewer",
            password=self.VIEWER_PASSWORD,
            role="viewer",
        )

        # 2. Simula o login para obter o token do viewer (usa a senha forte)
        login_response = self.client.post(
            self.login_url,
            {"email": viewer_user.email, "password": self.VIEWER_PASSWORD},
            format="json",
        )
        # Confirma que o login do viewer funciona (200 OK)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        viewer_token = login_response.data["access"]

        # 3. Payload COMPLETO, mas enviado por um usuário SEM permissão
        unauthorized_payload = {
            "email": "tentativa@fail.com",
            "name": "Falha Teste",
            "password": "viewerpassword",
            "role": "viewer",
        }

        # 4. Tenta criar um novo usuário com o token do viewer
        response = self.client.post(
            self.list_url,
            unauthorized_payload,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {viewer_token}",
        )

        # O teste deve falhar com 403 Forbidden (NÃO 201 Created)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
