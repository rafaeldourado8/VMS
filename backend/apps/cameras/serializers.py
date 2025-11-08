# Importa o validador de URL do Django
from django.core.validators import URLValidator
from rest_framework import serializers

from .models import Camera


class CameraSerializer(serializers.ModelSerializer):
    # Vamos exibir o email do dono, é mais útil no frontend
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    # Adiciona validação explícita para os campos de URL
    stream_url = serializers.CharField(max_length=1000, validators=[URLValidator()])

    # (CORRIGIDO) Usa 'allow_null=True' e 'required=False'
    # em vez de 'null=True' e 'blank=True'.
    thumbnail_url = serializers.CharField(
        max_length=1000,
        allow_null=True,  # O campo pode ser nulo na API
        required=False,  # O campo não é obrigatório no POST/PUT
        validators=[URLValidator()],
    )

    class Meta:
        model = Camera

        # Estes são os campos que sua API vai expor
        fields = [
            "id",
            "owner_email",  # Nosso campo personalizado
            "name",
            "location",
            "status",
            "stream_url",
            "thumbnail_url",  # Corrigido
            "latitude",
            "longitude",
            "detection_settings",
            "created_at",
        ]

        # O dono não pode ser mudado por uma API,
        # ele será definido automaticamente
        read_only_fields = ["id", "created_at", "owner_email"]
