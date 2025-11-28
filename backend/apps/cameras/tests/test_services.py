import pytest
from django.contrib.auth import get_user_model
from apps.cameras.services import CameraService
from apps.cameras.models import Camera

User = get_user_model()

@pytest.mark.django_db
class TestCameraService:
    def setup_method(self):
        # Configuração executada antes de cada teste
        self.service = CameraService()
        self.user = User.objects.create_user(
            email="teste@unitario.com", 
            name="Unit Tester", 
            password="PasswordForte123!"
        )

    def test_create_camera_success(self):
        """
        Testa se o serviço cria a câmara corretamente e associa ao utilizador (owner).
        """
        data = {
            "name": "Câmara Entrada",
            "stream_url": "rtsp://admin:12345@192.168.1.10:554/stream",
            "location": "Portão Principal"
        }

        # Executa a lógica
        camera = self.service.create_camera(self.user, data)

        # Asserções (Verificações)
        assert camera.id is not None
        assert camera.owner == self.user
        assert camera.name == "Câmara Entrada"
        assert camera.status == "online" # Verifica o default definido no model

    def test_list_cameras_isolation(self):
        """
        Garante que um utilizador NÃO vê câmaras de outro utilizador.
        """
        # 1. Cria câmara para o utilizador principal
        self.service.create_camera(self.user, {"name": "Minha Cam", "stream_url": "rtsp://x"})

        # 2. Cria outro utilizador e outra câmara
        other_user = User.objects.create_user(email="intruso@test.com", name="Intruso", password="123")
        self.service.create_camera(other_user, {"name": "Câmara do Intruso", "stream_url": "rtsp://y"})

        # 3. Busca câmaras do utilizador principal
        cameras = self.service.list_cameras_for_user(self.user)

        # 4. Verifica se apenas a câmara dele veio
        assert len(cameras) == 1
        assert cameras[0].name == "Minha Cam"