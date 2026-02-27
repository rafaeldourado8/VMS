from rest_framework import serializers
from .models import Clip

class ClipSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True, allow_null=True)
    camera_id = serializers.IntegerField(source='camera.id', read_only=True, allow_null=True)
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Clip
        fields = ['id', 'name', 'camera_id', 'camera_name', 'start_time', 'end_time', 
                 'file_path', 'video_url', 'thumbnail_path', 'duration_seconds', 
                 'status', 'created_at']
    
    def get_video_url(self, obj):
        return f"/api/clips/{obj.id}/video/"

class ClipCreateSerializer(serializers.Serializer):
    camera_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    quality = serializers.CharField(max_length=20, default='medium', required=False)