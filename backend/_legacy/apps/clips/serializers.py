from rest_framework import serializers
from .models import Clip, Mosaico, MosaicoCameraPosition
from apps.cameras.serializers import CameraSerializer

class ClipSerializer(serializers.ModelSerializer):
    camera = CameraSerializer(read_only=True)
    
    class Meta:
        model = Clip
        fields = ['id', 'name', 'camera', 'start_time', 'end_time', 
                 'file_path', 'thumbnail_path', 'duration_seconds', 'created_at']

class ClipCreateSerializer(serializers.Serializer):
    camera_id = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

class MosaicoCameraPositionSerializer(serializers.ModelSerializer):
    camera = CameraSerializer(read_only=True)
    
    class Meta:
        model = MosaicoCameraPosition
        fields = ['camera', 'position']

class MosaicoSerializer(serializers.ModelSerializer):
    cameras_positions = MosaicoCameraPositionSerializer(
        source='mosaicoCameraPosition_set', 
        many=True, 
        read_only=True
    )
    
    class Meta:
        model = Mosaico
        fields = ['id', 'name', 'cameras_positions', 'created_at', 'updated_at']