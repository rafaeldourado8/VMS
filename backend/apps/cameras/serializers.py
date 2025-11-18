# VMS/backend/apps/cameras/serializers.py

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from urllib.parse import urlparse, urlunparse, quote
import re

from .models import Camera

ALLOWED_SCHEMES = ['rtsp', 'rtspu', 'rtmp', 'http', 'https']


class CameraSerializer(serializers.ModelSerializer):
    # Vamos exibir o email do dono, é mais útil no frontend
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    # Mantemos CharField e validamos manualmente no método validate_stream_url
    stream_url = serializers.CharField(max_length=1000)

    # thumbnail: valida apenas http/https (se preferir aceitar mais, ajuste)
    thumbnail_url = serializers.CharField(
        max_length=1000,
        allow_null=True,
        required=False,
        validators=[URLValidator(schemes=['http', 'https'])],
    )

    stream_url_frontend = serializers.SerializerMethodField()

    def get_stream_url_frontend(self, obj):
        return obj.stream_url

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
            "latitude",
            "longitude",
            "detection_settings",
            "created_at",
            "stream_url_frontend",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "owner_email",
            "stream_url_frontend",
        ]

    def validate_stream_url(self, value: str) -> str:
        """
        Validação robusta para RTSP/RTMP/http(s).
        1) tenta URLValidator com schemes permitidos
        2) se falhar e houver credenciais, tenta percent-encode das credenciais
        3) fallback regex permissivo para formatos RTSP comuns
        """
        if not value:
            raise serializers.ValidationError("Stream URL não pode estar vazio.")

        raw = value.strip()
        parsed = urlparse(raw)

        if not parsed.scheme:
            raise serializers.ValidationError("Insira um URL válido (ex.: rtsp://...).")

        if parsed.scheme.lower() not in ALLOWED_SCHEMES:
            raise serializers.ValidationError(f"Esquema não suportado: {parsed.scheme}")

        validator = URLValidator(schemes=ALLOWED_SCHEMES)

        # 1) tenta validar direto
        try:
            validator(raw)
            return raw
        except DjangoValidationError:
            pass

        # 2) tenta reconstruir com percent-encoding de credenciais
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

        # 3) fallback regex permissivo para rtsp
        rtsp_regex = re.compile(r"^(rtsp|rtspu)://([^/\s]+)(/.*)?$", re.IGNORECASE)
        if rtsp_regex.match(raw):
            return raw

        raise serializers.ValidationError(
            "Insira um URL válido (ex.: rtsp://usuario:senha@ip:porta/caminho ou rtsp://ip:porta/caminho)."
        )