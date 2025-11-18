"""
Serializer Mixin para adicionar campos de streaming (MediaMTX / IA).
"""

from rest_framework import serializers
# Importa o novo serviço instanciado
from .services import streaming_integration_service as StreamingService


class StreamingSerializerMixin:
    """
    Mixin para adicionar campos de streaming a serializers (Câmera).
    
    Uso:
        class CameraSerializer(StreamingSerializerMixin, serializers.ModelSerializer):
            class Meta:
                model = Camera
                fields = '__all__'
    """
    
    # NOVO: URL WebRTC (WHEP) para o frontend
    webrtc_url = serializers.SerializerMethodField()
    
    # MANTIDO: URL do WebSocket para o serviço de IA
    ai_websocket_url = serializers.SerializerMethodField()
    
    # Obsoleto (has_active_stream não é mais rastreado aqui)
    # has_active_stream = serializers.SerializerMethodField()
    
    def get_webrtc_url(self, obj):
        """Retorna URL do stream WebRTC (WHEP) para o frontend."""
        return StreamingService.get_webrtc_url_for_frontend(obj)
    
    def get_ai_websocket_url(self, obj):
        """Retorna URL do WebSocket para o serviço de IA."""
        return StreamingService.get_ai_websocket_url(obj)
    
    # def get_has_active_stream(self, obj):
    #     """Verifica se tem stream ativo. (Obsoleto)"""
    #     return False