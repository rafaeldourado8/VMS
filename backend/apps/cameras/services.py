import logging
import httpx
from django.db import transaction
from django.conf import settings
from .models import Camera
from .schemas import CameraDTO

logger = logging.getLogger(__name__)

class CameraService:
    """Lógica de negócio e integração HTTP com o Streaming Service."""
    
    def __init__(self):
        # URL do serviço FastAPI de streaming definida no config/settings.py
        self.streaming_url = getattr(settings, 'STREAMING_SERVICE_URL', 'http://streaming:8001')

    def create_camera(self, data: CameraDTO) -> Camera:
        """Cria câmara no DB e provisiona no serviço de streaming."""
        with transaction.atomic():
            camera = Camera.objects.create(
                owner_id=data.owner_id,
                name=data.name,
                location=data.location,
                status=data.status,
                stream_url=data.stream_url,
                thumbnail_url=data.thumbnail_url,
                latitude=data.latitude,
                longitude=data.longitude,
                detection_settings=data.detection_settings
            )
        
        self._provision_streaming(camera)
        return camera

    def delete_camera(self, camera_id: int) -> None:
        """Remove câmara e limpa o path no serviço de streaming."""
        try:
            camera = Camera.objects.get(id=camera_id)
            self._remove_streaming(camera_id)
            camera.delete()
        except Camera.DoesNotExist:
            logger.warning(f"Câmara ID {camera_id} não encontrada para eliminação.")

    def list_cameras_for_user(self, user):
        return Camera.objects.filter(owner=user).order_by("-created_at")

    def _provision_streaming(self, camera: Camera):
        """Notifica o serviço externo para provisionar o stream."""
        try:
            httpx.post(
                f"{self.streaming_url}/cameras/provision",
                json={
                    "camera_id": camera.id,
                    "rtsp_url": camera.stream_url,
                    "name": camera.name
                },
                timeout=10.0
            )
        except Exception as e:
            logger.error(f"Falha ao provisionar stream {camera.id}: {str(e)}")

    def _remove_streaming(self, camera_id: int):
        """Solicita a remoção do stream no serviço externo."""
        try:
            httpx.delete(f"{self.streaming_url}/cameras/{camera_id}", timeout=5.0)
        except Exception as e:
            logger.error(f"Falha ao remover stream {camera_id}: {str(e)}")