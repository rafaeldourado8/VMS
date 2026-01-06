from rest_framework import serializers
from .models import VEHICLE_TYPE_CHOICES, Deteccao

class DeteccaoSerializer(serializers.ModelSerializer):
    """Serializer para leitura (Frontend)."""
    camera_name = serializers.CharField(source="camera.name", read_only=True)
    camera_id = serializers.IntegerField(source="camera.id", read_only=True)

    class Meta:
        model = Deteccao
        fields = ["id", "camera_id", "camera_name", "plate", "confidence", "timestamp", "vehicle_type", "image_url", "video_url"]

class IngestDeteccaoSerializer(serializers.Serializer):
    """Serializer para validação rigorosa dos dados de ingestão."""
    camera_id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    plate = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)
    confidence = serializers.FloatField(required=False, allow_null=True)
    vehicle_type = serializers.ChoiceField(choices=VEHICLE_TYPE_CHOICES, default="unknown")
    image_url = serializers.CharField(max_length=1000, required=False, allow_null=True)
    video_url = serializers.CharField(max_length=1000, required=False, allow_null=True)