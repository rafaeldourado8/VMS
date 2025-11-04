from rest_framework import serializers
from .models import Camera

class CameraSerializer(serializers.ModelSerializer):
    # owner = serializers.PrimaryKeyRelatedField(read_only=True)
    # Vamos exibir o email do dono, é mais útil no frontend
    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Camera

        # Estes são os campos que sua API vai expor
        # (Seção 3.1 e 3.2 da sua documentação)
        fields = [
            'id', 
            'owner_email', # Nosso campo personalizado
            'name', 
            'location', 
            'status', 
            'stream_url', 
            'thumbnail_url',
            'latitude', 
            'longitude', 
            'detection_settings', 
            'created_at'
        ]

        # O dono não pode ser mudado por uma API,
        # ele será definido automaticamente
        read_only_fields = ['id', 'created_at', 'owner_email']