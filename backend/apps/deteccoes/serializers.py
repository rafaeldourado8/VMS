from rest_framework import serializers
from .models import Deteccao

class DeteccaoSerializer(serializers.ModelSerializer):
    # Vamos "achatar" o relacionamento para bater com a API (Seção 4.1)
    # Em vez de um 'camera_id', vamos mostrar o 'camera_name'
    camera_name = serializers.CharField(source='camera.name', read_only=True)

    # Também vamos incluir o camera_id para o frontend, se ele precisar
    camera_id = serializers.IntegerField(source='camera.id', read_only=True)

    class Meta:
        model = Deteccao

        # Estes são os campos que sua API vai expor
        fields = [
            'id',
            'camera_id',    # Nosso campo extra
            'camera_name',  # Nosso campo extra
            'plate',
            'confidence',
            'timestamp',
            'vehicle_type',
            'image_url',
            'video_url',
        ]