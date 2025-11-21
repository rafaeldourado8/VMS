from abc import ABC, abstractmethod
from django.conf import settings
from apps.cameras.models import Camera
import logging

logger = logging.getLogger(__name__)

class StreamingProvider(ABC):
    @abstractmethod
    def get_frontend_stream_url(self, camera: Camera) -> str:
        pass

class MediaMTXProvider(StreamingProvider):
    def __init__(self, base_url: str):
        # Aqui 'base_url' deve vir como algo limpo, mas vamos forçar o HLS no método abaixo
        self.base_url = base_url

    def get_frontend_stream_url(self, camera: Camera) -> str:
        # MUDANÇA: Gerar URL HLS (http://dominio/hls/{id}/index.m3u8)
        # O Nginx vai capturar o /hls/ e mandar para a porta 8888 do MediaMTX
        return f"/hls/{camera.id}/index.m3u8"

class StreamingIntegrationService:
    def __init__(self, provider: StreamingProvider):
        self.provider = provider
        try:
            self.ai_base_url = getattr(settings, 'NGINX_AI_URL_BASE', '/ai')
        except AttributeError:
            self.ai_base_url = "/ai"
        logger.info(f"Streaming Service inicializado com provider: {type(provider).__name__}")

    def get_webrtc_url_for_frontend(self, camera: Camera) -> str:
        return self.provider.get_frontend_stream_url(camera)

    def get_ai_websocket_url(self, camera: Camera) -> str:
        base_url = self.ai_base_url.rstrip('/')
        return f"{base_url}/ws/detect/{camera.id}"

def get_streaming_service_instance():
    # Não usamos mais essa variável para a URL base do vídeo, pois forçamos /hls/ acima
    # mas mantemos a estrutura para não quebrar dependências
    webrtc_base_url = getattr(settings, 'NGINX_WEBRTC_URL_BASE', '/webrtc')
    provider = MediaMTXProvider(base_url=webrtc_base_url)
    return StreamingIntegrationService(provider)

streaming_integration_service = get_streaming_service_instance()