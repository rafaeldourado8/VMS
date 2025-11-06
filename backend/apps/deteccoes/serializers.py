from rest_framework import serializers

from apps.cameras.models import Camera

# 1. Importe 'VEHICLE_TYPE_CHOICES' diretamente dos modelos
from .models import VEHICLE_TYPE_CHOICES, Deteccao


class DeteccaoSerializer(serializers.ModelSerializer):
    """
    Serializer de LEITURA (Padrão).
    Usado para formatar os dados de detecção para o frontend.
    """

    camera_name = serializers.CharField(source="camera.name", read_only=True)
    camera_id = serializers.IntegerField(source="camera.id", read_only=True)

    class Meta:
        model = Deteccao
        fields = [
            "id",
            "camera_id",
            "camera_name",
            "plate",
            "confidence",
            "timestamp",
            "vehicle_type",
            "image_url",
            "video_url",
        ]


# --- Serializer de Ingestão (Refatoração SOLID) ---


class IngestDeteccaoSerializer(serializers.Serializer):
    """
    Serializer de ESCRITA (Ingestão).
    Tem a responsabilidade única de validar os dados brutos vindos do
    Lambda/Worker (ex: 'camera_id' em vez de um objeto 'camera').
    """

    camera_id = serializers.IntegerField()
    timestamp = serializers.DateTimeField()
    plate = serializers.CharField(
        max_length=20, required=False, allow_null=True, allow_blank=True
    )
    confidence = serializers.FloatField(required=False, allow_null=True)
    vehicle_type = serializers.ChoiceField(
        # 2. Corrigido: Use a variável importada, não o atributo da classe
        choices=VEHICLE_TYPE_CHOICES,
        default="unknown",
        required=False,
    )
    image_url = serializers.CharField(
        max_length=1000, required=False, allow_null=True, allow_blank=True
    )
    video_url = serializers.CharField(
        max_length=1000, required=False, allow_null=True, allow_blank=True
    )

    def validate_camera_id(self, value):
        """
        Verifica se a Câmera realmente existe no banco de dados.
        """
        try:
            camera_instance = Camera.objects.get(pk=value)
        except Camera.DoesNotExist:
            raise serializers.ValidationError(f"Câmera com id={value} não encontrada.")

        self.context["camera_instance"] = camera_instance
        return value

    def create(self, validated_data):
        """
        Cria o objeto Deteccao no banco de dados.
        """
        camera_instance = self.context["camera_instance"]
        validated_data.pop("camera_id")  # Remove o ID, pois usaremos o objeto

        return Deteccao.objects.create(camera=camera_instance, **validated_data)
