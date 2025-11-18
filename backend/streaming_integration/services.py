from django.conf import settings
from apps.cameras.models import Camera
import logging

logger = logging.getLogger(__name__)

class StreamingIntegrationService:
    def __init__(self):
        # O NGINX_STREAMING_URL_BASE (legado) foi substituído.
        
        # Esta é a URL base para o MediaMTX (WHEP), 
        # conforme definido no seu nginx.conf (ex: /webrtc)
        try:
            self.webrtc_base_url = settings.NGINX_WEBRTC_URL_BASE 
        except AttributeError:
            logger.error("NGINX_WEBRTC_URL_BASE não está definido no settings.py! Usando fallback '/webrtc'")
            self.webrtc_base_url = "/webrtc"

        # Esta é a URL base para o serviço de IA, que ainda é necessária
        # (ex: /ai)
        try:
            self.ai_base_url = settings.NGINX_AI_URL_BASE
        except AttributeError:
            logger.error("NGINX_AI_URL_BASE não está definido no settings.py! Usando fallback '/ai'")
            self.ai_base_url = "/ai"
            
        logger.info(
            f"StreamingIntegrationService (MediaMTX) inicializado. "
            f"Base WebRTC: {self.webrtc_base_url}, Base AI: {self.ai_base_url}"
        )

    def get_webrtc_url_for_frontend(self, camera: Camera) -> str:
        """
        Gera a URL WHEP (Egress) para o MediaMTX.
        O frontend usará esta URL para consumir o stream WebRTC.
        
        A configuração do Nginx (location /webrtc/) espera:
        /webrtc/{camera_id}/whep
        
        O Nginx remove o /webrtc/ e passa /{camera_id}/whep para o MediaMTX.
        """
        base_url = self.webrtc_base_url.rstrip('/')
        
        # O ID da câmera é o "path" do stream no MediaMTX
        return f"{base_url}/{camera.id}/whep"

    def get_ai_websocket_url(self, camera: Camera) -> str:
        """
        Gera a URL do WebSocket para o serviço de IA.
        (Esta função permanece, pois o serviço de IA ainda existe)
        Exemplo: /ai/ws/detect/cam1
        """
        base_url = self.ai_base_url.rstrip('/')
        return f"{base_url}/ws/detect/{camera.id}"

    # --- MÉTODOS OBSOLETOS ---
    # get_stream_url_for_frontend (removido, era para HLS)
    # get_websocket_url (removido, era para o WebSocket de vídeo legado)

# Instancia o serviço atualizado
streaming_integration_service = StreamingIntegrationService()