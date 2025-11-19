"""
Serializer Mixin para adicionar campos de streaming (MediaMTX / IA).
"""

from rest_framework import serializers

# NOTA: Removemos a importação global do serviço para evitar Circular Import
# from .services import streaming_integration_service

class StreamingSerializerMixin:
    """
    Mixin para adicionar campos de streaming a serializers (Câmera).
    
    Uso:
        class CameraSerializer(StreamingSerializerMixin, serializers.ModelSerializer):
            class Meta:
                model = Camera
                fields = '__all__'
    """
    
    # URL WebRTC (WHEP) para o frontend
    webrtc_url = serializers.SerializerMethodField()
    
    # URL do WebSocket para o serviço de IA
    ai_websocket_url = serializers.SerializerMethodField()
    
    def get_webrtc_url(self, obj):
        """Retorna URL do stream WebRTC (WHEP) para o frontend."""
        # --- CORREÇÃO: Lazy Import ---
        # Importamos aqui dentro para quebrar o ciclo de dependência:
        # CameraSerializer -> StreamingSerializer -> Services -> CameraModel
        from .services import streaming_integration_service
        return streaming_integration_service.get_webrtc_url_for_frontend(obj)
    
    def get_ai_websocket_url(self, obj):
        """Retorna URL do WebSocket para o serviço de IA."""
        # --- CORREÇÃO: Lazy Import ---
        from .services import streaming_integration_service
        return streaming_integration_service.get_ai_websocket_url(obj)