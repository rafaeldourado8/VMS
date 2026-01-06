from rest_framework import serializers
from django.urls import reverse
from .models import Camera

class CameraSerializer(serializers.ModelSerializer):
    """Serializer com URLs dinâmicas para o Frontend."""
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    stream_url_frontend = serializers.SerializerMethodField()
    ai_websocket_url = serializers.SerializerMethodField() 
    snapshot_url = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = [
            "id", "owner_email", "name", "location", "status",
            "stream_url", "thumbnail_url", "snapshot_url",
            "latitude", "longitude", "detection_settings", "created_at",
            "stream_url_frontend", "ai_websocket_url", 
        ]
        read_only_fields = ["id", "created_at", "snapshot_url"]

    def get_stream_url_frontend(self, obj):
        # Rota HLS/WebRTC via HAProxy
        return f"/ws/live/camera_{obj.id}"

    def get_ai_websocket_url(self, obj):
        # Rota de IA via HAProxy
        return f"/ai/stream/{obj.id}"

    def get_snapshot_url(self, obj):
        request = self.context.get('request')
        try:
            url = reverse('camera-snapshot', kwargs={'camera_id': obj.id})
            return request.build_absolute_uri(url) if request else url
        except:
            return None