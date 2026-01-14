from rest_framework import serializers
from .models import Usuario


class PlanInfoSerializer(serializers.Serializer):
    """Serializer para informações do plano do usuário"""
    plan = serializers.CharField()
    recording_days = serializers.IntegerField()
    max_cameras = serializers.IntegerField()
    max_clips = serializers.IntegerField()
    max_concurrent_streams = serializers.IntegerField()
    current_cameras = serializers.IntegerField()
    can_add_camera = serializers.BooleanField()
