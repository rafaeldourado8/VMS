from abc import ABC, abstractmethod
from django.conf import settings
from apps.cameras.models import Camera
import logging

logger = logging.getLogger(__name__)

class StreamingProvider(ABC):
    """
    Interface que define como obter URLs de streaming.
    Qualquer tecnologia de streaming nova deve implementar esta classe.
    """
    @abstractmethod
    def get_frontend_stream_url(self, camera: Camera) -> str:
        pass

class MediaMTXProvider(StreamingProvider):
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_frontend_stream_url(self, camera: Camera) -> str:
        """
        Gera a URL WHEP para o MediaMTX.
        """
        base = self.base_url.rstrip('/')
        # O ID da câmara é o path no MediaMTX
        return f"{base}/{camera.id}/whep"

class StreamingIntegrationService:
    def __init__(self, provider: StreamingProvider):
        self.provider = provider
        
        # URL base para o serviço de IA (ainda necessário separadamente)
        try:
            self.ai_base_url = getattr(settings, 'NGINX_AI_URL_BASE', '/ai')
        except AttributeError:
            self.ai_base_url = "/ai"
            
        logger.info(f"Streaming Service inicializado com provider: {type(provider).__name__}")

    def get_webrtc_url_for_frontend(self, camera: Camera) -> str:
        """Delega a geração da URL para o provider configurado."""
        return self.provider.get_frontend_stream_url(camera)

    def get_ai_websocket_url(self, camera: Camera) -> str:
        """Gera URL para o WebSocket de IA."""
        base_url = self.ai_base_url.rstrip('/')
        return f"{base_url}/ws/detect/{camera.id}"


def get_streaming_service_instance():
    """
    Lê as configurações e instancia o provider correto.
    """
    # Lógica para decidir qual provider usar (pode vir de .env)
    webrtc_base_url = getattr(settings, 'NGINX_WEBRTC_URL_BASE', '/webrtc')
    
    # Instancia o MediaMTXProvider (poderia ser outro aqui)
    provider = MediaMTXProvider(base_url=webrtc_base_url)
    
    return StreamingIntegrationService(provider)

streaming_integration_service = get_streaming_service_instance()