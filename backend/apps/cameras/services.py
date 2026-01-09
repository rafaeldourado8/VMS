"""
GT-Vision - Camera Service (Corrigido)
======================================
Lógica de negócio e integração HTTP com o Streaming Service.
Câmeras são provisionadas dinamicamente no MediaMTX via API.
"""

import logging
import httpx
from django.db import transaction
from django.conf import settings
from django.core.cache import cache
from .models import Camera
from .schemas import CameraDTO

logger = logging.getLogger(__name__)

class StreamLimiter:
    """Controla limites de streams simultâneos por usuário."""
    
    @staticmethod
    def can_start_stream(user_id: int, max_streams: int) -> bool:
        key = f"user_streams:{user_id}"
        current = cache.get(key, 0)
        return current < max_streams
    
    @staticmethod
    def increment_stream(user_id: int) -> None:
        key = f"user_streams:{user_id}"
        current = cache.get(key, 0)
        cache.set(key, current + 1, timeout=None)
    
    @staticmethod
    def decrement_stream(user_id: int) -> None:
        key = f"user_streams:{user_id}"
        current = cache.get(key, 0)
        if current > 0:
            cache.set(key, current - 1, timeout=None)
    
    @staticmethod
    def get_current_streams(user_id: int) -> int:
        key = f"user_streams:{user_id}"
        return cache.get(key, 0)

class CameraService:
    """Lógica de negócio e integração HTTP com o Streaming Service."""
    
    def __init__(self):
        # URL do serviço FastAPI de streaming definida no config/settings.py
        self.streaming_url = getattr(settings, 'STREAMING_SERVICE_URL', 'http://streaming:8001')
        self.timeout = 15.0  # Timeout aumentado para provisionamento

    def create_camera(self, data: CameraDTO) -> Camera:
        """
        Cria câmara no DB e provisiona no serviço de streaming.
        
        Fluxo:
        1. Salva no banco de dados (Django)
        2. Notifica o Streaming Service para provisionar no MediaMTX
        3. Se falhar no streaming, a câmera ainda existe no DB (pode reprovisionar depois)
        """
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
        
        # Provisiona no MediaMTX via Streaming Service
        success = self._provision_streaming(camera)
        
        if success:
            logger.info(f"✅ Câmera {camera.id} ({camera.name}) criada e provisionada com sucesso")
        else:
            logger.warning(f"⚠️ Câmera {camera.id} criada no DB, mas falhou no provisionamento. "
                          f"Use POST /streaming/cameras/provision para reprovisionar.")
        
        return camera

    def delete_camera(self, camera_id: int) -> None:
        """Remove câmara e limpa o path no serviço de streaming."""
        try:
            camera = Camera.objects.get(id=camera_id)
            
            # Remove do MediaMTX primeiro
            self._remove_streaming(camera_id)
            
            # Depois remove do banco
            camera.delete()
            logger.info(f"✅ Câmera {camera_id} removida completamente")
            
        except Camera.DoesNotExist:
            logger.warning(f"Câmara ID {camera_id} não encontrada para eliminação.")

    def list_cameras_for_user(self, user):
        """Lista câmeras do usuário ordenadas por data de criação."""
        return Camera.objects.filter(owner=user).order_by("-created_at")

    def reprovision_all_cameras(self, user=None) -> dict:
        """
        Reprovisiona todas as câmeras no MediaMTX.
        Útil após restart do MediaMTX ou para sincronizar estado.
        
        Args:
            user: Se informado, reprovisiona apenas câmeras deste usuário
            
        Returns:
            Dict com contadores de sucesso/falha
        """
        if user:
            cameras = Camera.objects.filter(owner=user)
        else:
            cameras = Camera.objects.all()
        
        results = {"success": 0, "failed": 0, "total": cameras.count()}
        
        for camera in cameras:
            if self._provision_streaming(camera):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"Reprovisionamento: {results['success']}/{results['total']} câmeras OK")
        return results

    def _provision_streaming(self, camera: Camera) -> bool:
        """
        Notifica o serviço externo para provisionar o stream no MediaMTX.
        
        Args:
            camera: Instância da câmera a provisionar
            
        Returns:
            True se provisionou com sucesso, False caso contrário
        """
        payload = {
            "camera_id": camera.id,
            "rtsp_url": camera.stream_url,
            "name": camera.name,
            "on_demand": True  # Só conecta quando há viewers
        }
        
        try:
            logger.debug(f"Provisionando câmera {camera.id} em {self.streaming_url}/cameras/provision")
            
            response = httpx.post(
                f"{self.streaming_url}/cameras/provision",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    logger.info(f"📹 Stream provisionado: {data.get('stream_path')} -> {data.get('hls_url')}")
                    return True
                else:
                    logger.error(f"Falha no provisionamento: {data.get('message')}")
                    return False
            else:
                logger.error(f"Erro HTTP {response.status_code}: {response.text}")
                return False
                
        except httpx.TimeoutException:
            logger.error(f"Timeout ao provisionar câmera {camera.id} (>{self.timeout}s)")
            return False
        except httpx.ConnectError:
            logger.error(f"Não foi possível conectar ao Streaming Service em {self.streaming_url}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado ao provisionar stream {camera.id}: {str(e)}")
            return False

    def _remove_streaming(self, camera_id: int) -> bool:
        """
        Solicita a remoção do stream no serviço externo.
        
        Args:
            camera_id: ID da câmera a remover
            
        Returns:
            True se removeu com sucesso, False caso contrário
        """
        try:
            response = httpx.delete(
                f"{self.streaming_url}/cameras/{camera_id}", 
                timeout=self.timeout
            )
            
            if response.status_code in [200, 404]:
                # 404 = já não existe, tudo bem
                logger.info(f"🗑️ Stream cam_{camera_id} removido do MediaMTX")
                return True
            else:
                logger.error(f"Erro ao remover stream {camera_id}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Falha ao remover stream {camera_id}: {str(e)}")
            return False

    def get_camera_stream_status(self, camera_id: int) -> dict:
        """
        Consulta o status do stream de uma câmera específica.
        
        Returns:
            Dict com status do stream (ready, viewers, etc)
        """
        try:
            response = httpx.get(
                f"{self.streaming_url}/cameras/{camera_id}/status",
                timeout=5.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "unknown", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}