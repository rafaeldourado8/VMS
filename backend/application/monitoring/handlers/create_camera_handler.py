import os
import logging
import requests
from ..commands.create_camera_command import CreateCameraCommand

from domain.monitoring.entities.camera import Camera
from domain.monitoring.repositories.camera_repository import CameraRepository
from domain.monitoring.value_objects.geo_coordinates import GeoCoordinates
from domain.monitoring.value_objects.location import Location
from domain.monitoring.value_objects.stream_url import StreamUrl

logger = logging.getLogger(__name__)

class CreateCameraHandler:
    """Handler para criar câmera"""
    
    def __init__(self, repository: CameraRepository):
        self.repository = repository
        self.streaming_service_url = os.getenv('STREAMING_SERVICE_URL', 'http://streaming:8001')
    
    def handle(self, command: CreateCameraCommand) -> Camera:
        """Executa o use case de criar câmera"""
        
        camera = Camera(
            id=None,
            owner_id=command.owner_id,
            name=command.name,
            stream_url=StreamUrl(command.stream_url),
            location=Location(command.location),
            coordinates=GeoCoordinates(command.latitude, command.longitude),
            thumbnail_url=command.thumbnail_url
        )
        
        saved_camera = self.repository.save(camera)
        
        # Ativa IA automaticamente se for RTSP
        if command.stream_url.lower().startswith('rtsp://'):
            from apps.cameras.models import Camera as CameraModel
            camera_model = CameraModel.objects.get(id=saved_camera.id)
            camera_model.ai_enabled = True
            camera_model.save()
            logger.info(f"🤖 IA ativada automaticamente para câmera RTSP {saved_camera.id}")
            
            # Notifica LPR service
            try:
                requests.post(
                    'http://lpr_detection:5000/camera/start',
                    json={'camera_id': saved_camera.id, 'rtsp_url': command.stream_url},
                    timeout=2
                )
                logger.info(f"📡 LPR service notificado para câmera {saved_camera.id}")
            except Exception as e:
                logger.warning(f"⚠️ Falha ao notificar LPR: {e}")
        
        # Provisiona stream no MediaMTX via Streaming Service
        try:
            logger.info(f"🎥 Provisionando stream para câmera {saved_camera.id}")
            response = requests.post(
                f"{self.streaming_service_url}/cameras/provision",
                json={
                    "camera_id": saved_camera.id,
                    "rtsp_url": command.stream_url,
                    "name": command.name,
                    "on_demand": True
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Stream provisionado com sucesso para câmera {saved_camera.id}")
            else:
                logger.warning(f"⚠️ Falha ao provisionar stream: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"❌ Erro ao provisionar stream: {e}")
        
        return saved_camera
