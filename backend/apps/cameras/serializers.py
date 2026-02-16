from rest_framework import serializers
from django.urls import reverse
import logging
import re
from .models import Camera

logger = logging.getLogger(__name__)

class CameraSerializer(serializers.ModelSerializer):
    """Serializer com URLs dinâmicas para o Frontend."""
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    stream_url_frontend = serializers.SerializerMethodField()
    ai_websocket_url = serializers.SerializerMethodField() 
    snapshot_url = serializers.SerializerMethodField()
    recording_retention_days = serializers.IntegerField(default=30, required=False)
    
    # Campos opcionais de endereço
    address_street = serializers.CharField(required=False, allow_blank=True)
    address_number = serializers.CharField(required=False, allow_blank=True)
    address_neighborhood = serializers.CharField(required=False, allow_blank=True)
    address_city = serializers.CharField(required=False, allow_blank=True)
    address_state = serializers.CharField(required=False, allow_blank=True)
    maps_url = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Camera
        fields = [
            "id", "owner_email", "name", "location", "status",
            "stream_url", "thumbnail_url", "snapshot_url",
            "latitude", "longitude", "detection_settings", "created_at",
            "stream_url_frontend", "ai_websocket_url", "recording_retention_days",
            "address_street", "address_number", "address_neighborhood", 
            "address_city", "address_state", "maps_url", "timezone",
        ]
        read_only_fields = ["id", "created_at", "snapshot_url"]
        extra_kwargs = {
            'location': {'required': False, 'allow_blank': True}
        }
    
    def validate(self, data):
        logger.info(f"Serializer validating data: {data}")
        
        # Extrair coordenadas de URL do Google Maps
        if 'maps_url' in data and data['maps_url']:
            coords = self._extract_coordinates_from_url(data['maps_url'])
            if coords:
                data['latitude'] = coords['latitude']
                data['longitude'] = coords['longitude']
        
        # Construir location a partir do endereço estruturado
        if any(k in data for k in ['address_street', 'address_city']):
            parts = []
            if data.get('address_street'):
                street = data['address_street']
                if data.get('address_number'):
                    street += f", {data['address_number']}"
                parts.append(street)
            if data.get('address_neighborhood'):
                parts.append(data['address_neighborhood'])
            if data.get('address_city'):
                parts.append(data['address_city'])
            if data.get('address_state'):
                parts.append(data['address_state'])
            if parts:
                data['location'] = ' - '.join(parts)
        
        # Se location ainda estiver vazio, usar coordenadas ou nome
        if not data.get('location'):
            if data.get('latitude') and data.get('longitude'):
                data['location'] = f"{data['latitude']}, {data['longitude']}"
            else:
                data['location'] = data.get('name', 'Sem localização')
        
        return data
    
    def _extract_coordinates_from_url(self, url):
        """Extrai coordenadas de URL do Google Maps"""
        patterns = [
            r'@([+-]?\d+\.\d+),([+-]?\d+\.\d+)',  # @-20.5039951,-54.6228302
            r'!3d([+-]?\d+\.\d+)!4d([+-]?\d+\.\d+)',  # !3d-20.5039951!4d-54.6228302
            r'[?&]q=([+-]?\d+\.\d+),([+-]?\d+\.\d+)',  # ?q=-20.5039951,-54.6228302
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return {
                    'latitude': float(match.group(1)),
                    'longitude': float(match.group(2))
                }
        return None

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