from rest_framework import serializers

class StreamingSerializerMixin:
    webrtc_url = serializers.SerializerMethodField()
    ai_websocket_url = serializers.SerializerMethodField()

    def get_webrtc_url(self, obj):
        from .services import streaming_integration_service
        return streaming_integration_service.get_webrtc_url_for_frontend(obj)

    def get_ai_websocket_url(self, obj):
        from .services import streaming_integration_service
        return streaming_integration_service.get_ai_websocket_url(obj)