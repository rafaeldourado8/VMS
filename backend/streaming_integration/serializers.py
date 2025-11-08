"""
Serializer Mixin para adicionar campos de streaming.
"""

from rest_framework import serializers
from .services import StreamingService


class StreamingSerializerMixin:
    """
    Mixin para adicionar campos de streaming a serializers.
    
    Uso:
        class CameraSerializer(StreamingSerializerMixin, serializers.ModelSerializer):
            class Meta:
                model = Camera
                fields = '__all__'
    """
    
    stream_url_frontend = serializers.SerializerMethodField()
    websocket_url = serializers.SerializerMethodField()
    has_active_stream = serializers.SerializerMethodField()
    
    def get_stream_url_frontend(self, obj):
        """Retorna URL do stream para o frontend."""
        return StreamingService.get_stream_url_for_frontend(obj)
    
    def get_websocket_url(self, obj):
        """Retorna URL do WebSocket."""
        return StreamingService.get_websocket_url(obj)
    
    def get_has_active_stream(self, obj):
        """Verifica se tem stream ativo."""
        return hasattr(obj, 'stream_id') and obj.stream_id is not None