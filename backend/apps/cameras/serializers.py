from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from urllib.parse import urlparse, urlunparse, quote
from django.urls import reverse  # Import necessário
import re
from django.conf import settings

from .models import Camera
from streaming_integration.serializers import StreamingSerializerMixin

ALLOWED_SCHEMES = ['rtsp', 'rtspu', 'rtmp', 'http', 'https']

class CameraSerializer(StreamingSerializerMixin, serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    stream_url = serializers.CharField(max_length=1000)
    thumbnail_url = serializers.CharField(
        max_length=1000,
        allow_null=True,
        required=False,
        validators=[URLValidator(schemes=['http', 'https'])],
    )
    
    # Mantemos este campo para compatibilidade com o frontend
    stream_url_frontend = serializers.SerializerMethodField()

    # WebSocket URL para IA
    ai_websocket_url = serializers.SerializerMethodField() 

    # --- NOVO CAMPO: URL para o Snapshot Dinâmico ---
    snapshot_url = serializers.SerializerMethodField()

    def get_stream_url_frontend(self, obj):
        # Reutiliza a lógica centralizada no Mixin
        return self.get_webrtc_url(obj)

    def get_snapshot_url(self, obj):
        """
        Gera a URL completa para o endpoint de snapshot da câmera.
        Ex: http://localhost:8000/api/thumbnails/1/
        """
        request = self.context.get('request')
        url = reverse('camera-snapshot', kwargs={'camera_id': obj.id})
        if request:
            return request.build_absolute_uri(url)
        return url

    class Meta:
        model = Camera
        fields = [
            "id",
            "owner_email",
            "name",
            "location",
            "status",
            "stream_url",
            "thumbnail_url",
            "snapshot_url", # Novo campo exposto
            "latitude",
            "longitude",
            "detection_settings",
            "created_at",
            # Campos computados
            "stream_url_frontend",
            "ai_websocket_url", 
        ]
        read_only_fields = [
            "id",
            "created_at",
            "owner_email",
            "stream_url_frontend",
            "ai_websocket_url",
            "snapshot_url",
        ]

    def validate_stream_url(self, value: str) -> str:
        if not value:
            raise serializers.ValidationError("Stream URL não pode estar vazio.")

        raw = value.strip()
        parsed = urlparse(raw)

        if not parsed.scheme:
            raise serializers.ValidationError("Insira um URL válido (ex.: rtsp://...).")

        if parsed.scheme.lower() not in ALLOWED_SCHEMES:
            raise serializers.ValidationError(f"Esquema não suportado: {parsed.scheme}")

        validator = URLValidator(schemes=ALLOWED_SCHEMES)

        try:
            validator(raw)
            return raw
        except DjangoValidationError:
            pass

        try:
            if parsed.username or parsed.password:
                username = quote(parsed.username) if parsed.username else ''
                password = quote(parsed.password) if parsed.password else ''
                auth = f"{username}:{password}@" if (username or password) else ''
                hostport = parsed.hostname or ''
                if parsed.port:
                    hostport += f":{parsed.port}"
                new_netloc = f"{auth}{hostport}"
                rebuilt = urlunparse((
                    parsed.scheme,
                    new_netloc,
                    parsed.path or '',
                    parsed.params or '',
                    parsed.query or '',
                    parsed.fragment or '',
                ))
                try:
                    validator(rebuilt)
                    return rebuilt
                except DjangoValidationError:
                    pass
        except Exception:
            pass

        rtsp_regex = re.compile(r"^(rtsp|rtspu)://([^/\s]+)(/.*)?$", re.IGNORECASE)
        if rtsp_regex.match(raw):
            return raw

        raise serializers.ValidationError(
            "Insira um URL válido (ex.: rtsp://usuario:senha@ip:porta/caminho ou rtsp://ip:porta/caminho)."
        )