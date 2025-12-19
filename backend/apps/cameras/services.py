import logging
import httpx
from typing import List
from django.db import transaction
from django.conf import settings
from .models import Camera
from .schemas import CameraDTO

logger = logging.getLogger(__name__)

class CameraService:
    """Lógica de negócio para Câmaras e integração com Streaming Service."""
    
    def __init__(self):
        self.streaming_url = getattr(settings, 'STREAMING_SERVICE_URL', 'http://streaming:8001')

    def create_camera(self, data: CameraDTO) -> Camera:
        """Cria câmara no DB e provisiona o stream no serviço dedicado."""
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
        
        # Notificar o serviço de streaming (Async ou via Thread seria ideal, mas aqui segue o plano)
        self._provision_streaming(camera)
        return camera

    def delete_camera(self, camera_id: int) -> None:
        """Remove câmara do DB e encerra o stream no serviço de streaming."""
        try:
            camera = Camera.objects.get(id=camera_id)
            self._remove_streaming(camera_id)
            camera.delete()
        except Camera.DoesNotExist:
            logger.warning(f"Tentativa de eliminar câmara inexistente ID: {camera_id}")

    def list_cameras_for_user(self, user):
        """Lista as câmaras pertencentes a um utilizador específico."""
        return Camera.objects.filter(owner=user).order_by("-created_at")

    def _provision_streaming(self, camera: Camera):
        """Chama o Streaming Service para registar o path no MediaMTX."""
        try:
            response = httpx.post(
                f"{self.streaming_url}/cameras/provision",
                json={
                    "camera_id": camera.id,
                    "rtsp_url": camera.stream_url,
                    "name": camera.name
                },
                timeout=10.0
            )
            response.raise_for_status()
            logger.info(f"Stream provisionado para câmara {camera.id}")
        except Exception as e:
            logger.error(f"Erro ao provisionar stream para câmara {camera.id}: {str(e)}")

    def _remove_streaming(self, camera_id: int):
        """Solicita a remoção do path no Streaming Service."""
        try:
            httpx.delete(f"{self.streaming_url}/cameras/{camera_id}", timeout=5.0)
        except Exception as e:
            logger.error(f"Erro ao remover stream da câmara {camera_id}: {str(e)}")