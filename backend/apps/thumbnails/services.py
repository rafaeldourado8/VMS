import logging
import subprocess
from django.core.cache import cache
from apps.cameras.models import Camera

logger = logging.getLogger(__name__)

class ThumbnailService:
    def get_snapshot(self, camera_id: int) -> bytes | None:
        """
        Gera um snapshot da câmara usando FFmpeg.
        Utiliza Redis para cachear a imagem por 30 segundos.
        """
        # 1. Tenta pegar do Cache (Rápido)
        cache_key = f"camera_snapshot_{camera_id}"
        cached_image = cache.get(cache_key)

        if cached_image:
            return cached_image

        # 2. Busca a câmara no banco
        try:
            camera = Camera.objects.get(id=camera_id)
        except Camera.DoesNotExist:
            return None

        rtsp_url = camera.stream_url
        if not rtsp_url:
            return None

        # 3. Extrai do Stream (Lento - FFmpeg)
        # -rtsp_transport tcp: Evita corrupção de imagem
        # -vframes 1: Pega apenas 1 quadro
        # -vf scale=640:-1: Redimensiona para leveza (HD é desnecessário para thumb)
        command = [
            'ffmpeg',
            '-y',
            '-rtsp_transport', 'tcp',
            '-i', rtsp_url,
            '-f', 'image2',
            '-vframes', '1',
            '-vf', 'scale=640:-1', 
            '-update', '1',
            'pipe:1' # Saída no stdout
        ]

        try:
            # Timeout agressivo (5s) para não travar workers
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            output, error = process.communicate(timeout=5)

            if process.returncode == 0 and output:
                # Salva no cache por 30 segundos para evitar spam no RTSP
                cache.set(cache_key, output, timeout=30)
                return output
            else:
                # Log de erro apenas se falhar
                err_msg = error.decode('utf-8') if error else 'Sem saída de erro'
                logger.error(f"Erro FFmpeg (Cam {camera.id}): {err_msg}")
                return None

        except subprocess.TimeoutExpired:
            process.kill()
            logger.warning(f"Timeout ao gerar snapshot para câmara {camera.id}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado no snapshot: {e}")
            return None