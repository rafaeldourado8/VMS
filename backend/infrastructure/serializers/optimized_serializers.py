from rest_framework import serializers

class OptimizedCameraSerializer(serializers.Serializer):
    """Serializer otimizado para câmeras"""
    
    id = serializers.IntegerField()
    name = serializers.CharField()
    status = serializers.CharField()
    location = serializers.CharField()

class OptimizedDetectionSerializer(serializers.Serializer):
    """Serializer otimizado para detecções"""
    
    id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    vehicle_type = serializers.CharField()
    camera_name = serializers.CharField()

class AnalyticsSerializer(serializers.Serializer):
    """Serializer para dados de analytics"""
    
    total_detections = serializers.IntegerField()
    active_cameras = serializers.IntegerField()
    period = serializers.CharField()