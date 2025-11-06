# # VMS/backend/apps/dashboard/tests.py

# from django.utils import timezone
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# from django.contrib.auth import get_user_model
# from apps.cameras.models import Camera
# from apps.deteccoes.models import Deteccao

# User = get_user_model()


# class DashboardAPITest(APITestCase):
#     def setUp(self):
#         """Configura o banco de dados de teste com dados simulados."""

#         # 1. Cria o usuário e a câmera (como fizemos no shell)
#         self.user = User.objects.create_user(
#             email="testuser@gt.com",
#             name="Test User",
#             password="testpassword",
#             role="admin",  # Admin para garantir acesso
#         )
#         self.camera = Camera.objects.create(
#             owner=self.user, name="Câmera Teste 1", stream_url="rtsp://teste.com/stream"
#         )

#         # 2. Cria detecções
#         Deteccao.objects.create(
#             camera=self.camera,
#             plate="ABC-1234",
#             vehicle_type="car",
#             timestamp=timezone.now(),
#         )
#         Deteccao.objects.create(
#             camera=self.camera,
#             plate="DEF-5678",
#             vehicle_type="truck",
#             timestamp=timezone.now(),
#         )

#         # 3. Força a autenticação do cliente de teste
#         self.client.force_authenticate(user=self.user)

#         # 4. Define as URLs
#         self.stats_url = reverse("dashboard-stats")
#         self.events_url = reverse("dashboard-recent-events")

#     def test_stats_api_view(self):
#         """Testa o Endpoint 2.1: Estatísticas Gerais"""
#         response = self.client.get(self.stats_url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Valida os dados agregados
#         self.assertEqual(response.data["total_cameras"], 1)
#         self.assertEqual(response.data["online_cameras"], 0)  # O default é 'offline'
#         self.assertEqual(response.data["total_detections_today"], 2)

#     def test_recent_events_api_view(self):
#         """Testa o Endpoint 2.2: Eventos Recentes"""
#         response = self.client.get(self.events_url)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Valida a lista de eventos
#         self.assertEqual(len(response.data["events"]), 2)
#         self.assertEqual(
#             response.data["events"][0]["plate"], "DEF-5678"
#         )  # O mais recente (ou ABC-1234)
