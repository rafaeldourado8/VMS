import logging
import subprocess
from django.core.cache import cache
from apps.cameras.models import Camera

logger = logging.getLogger(__name__)

class ThumbnailService:
    """Serviço para geração de snapshots em tempo real via FFmpeg."""

    def get_snapshot(self, camera_id: int) -> bytes | None:
        """
        Gera um snapshot da câmara. 
        Cacheia a imagem por 30 segundos para otimizar recursos.
        """
        cache_key = f"camera_snapshot_{camera_id}"
        cached_image = cache.get(cache_key)

        if cached_image:
            return cached_image

        try:
            camera = Camera.objects.get(id=camera_id)
        except Camera.DoesNotExist:
            return None

        rtsp_url = camera.stream_url
        if not rtsp_url:
            return None

        # Comando FFmpeg para capturar 1 frame via TCP
        command = [
            'ffmpeg', '-y', '-rtsp_transport', 'tcp',
            '-i', rtsp_url, '-f', 'image2', '-vframes', '1',
            '-vf', 'scale=640:-1', '-update', '1', 'pipe:1'
        ]

        try:
            process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            output, error = process.communicate(timeout=5)

            if process.returncode == 0 and output:
                cache.set(cache_key, output, timeout=30)
                return output
            
            logger.error(f"Erro FFmpeg (Cam {camera_id}): {error.decode('utf-8')}")
            return None

        except subprocess.TimeoutExpired:
            process.kill()
            logger.warning(f"Timeout ao gerar snapshot para câmara {camera_id}")
            return None