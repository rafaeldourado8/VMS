import os
from rest_framework import serializers
from .models import Recording

class RecordingSerializer(serializers.ModelSerializer):
    hls_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Recording
        fields = '__all__'
    
    def get_hls_url(self, obj):
        """Gera URL HLS para o VOD Service"""
        vod_url = os.getenv('VOD_SERVICE_URL', 'http://vod_hls:8004')
        # Formato: /vod/{camera_id}/{date}/{filename}/index.m3u8
        return f"{vod_url}/vod/camera_{obj.camera_id}/{obj.date}/{obj.file_name}/index.m3u8"
