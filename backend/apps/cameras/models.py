from django.conf import settings
from django.db import models
from apps.iam.mixins import TenantAwareMixin, TenantAwareManager

STATUS_CHOICES = (("online", "Online"), ("offline", "Offline"))

class Camera(TenantAwareMixin, models.Model):
    """Modelo de persistência de Câmaras."""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cameras",
    )
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=1000)
    # Endereço estruturado
    address_street = models.CharField(max_length=255, blank=True, null=True)
    address_number = models.CharField(max_length=20, blank=True, null=True)
    address_neighborhood = models.CharField(max_length=100, blank=True, null=True)
    address_city = models.CharField(max_length=100, blank=True, null=True)
    address_state = models.CharField(max_length=2, blank=True, null=True)
    # Coordenadas
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    # URL do Google Maps
    maps_url = models.CharField(max_length=1000, blank=True, null=True)
    # Timezone da câmera (ex: America/Sao_Paulo)
    timezone = models.CharField(max_length=50, default="America/Sao_Paulo")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="online")
    stream_url = models.CharField(max_length=1000)
    stream_key = models.CharField(max_length=32, unique=True, blank=True, null=True, help_text="Chave unica para RTMP push")
    device_id = models.CharField(max_length=100, blank=True, null=True, help_text="DeviceID da camera para webhook push")
    brand = models.CharField(max_length=50, blank=True, null=True, help_text="Marca da camera (hikvision, intelbras)")
    model_name = models.CharField(max_length=100, blank=True, null=True, help_text="Modelo da camera")
    thumbnail_url = models.CharField(max_length=1000, blank=True, null=True)
    
    # Credenciais ONVIF para playback
    onvif_host = models.CharField(max_length=255, blank=True, null=True, help_text="IP ou hostname da câmera")
    onvif_port = models.IntegerField(default=80, help_text="Porta ONVIF (geralmente 80)")
    onvif_username = models.CharField(max_length=255, blank=True, null=True)
    onvif_password = models.CharField(max_length=255, blank=True, null=True)
    
    detection_settings = models.JSONField(default=dict, blank=True, null=True)
    # Configurações de detecção avançadas
    roi_areas = models.JSONField(default=list, blank=True, null=True)  # Áreas ROI
    virtual_lines = models.JSONField(default=list, blank=True, null=True)  # Linhas virtuais
    tripwires = models.JSONField(default=list, blank=True, null=True)  # Tripwires
    zone_triggers = models.JSONField(default=list, blank=True, null=True)  # Zonas de trigger
    # Configurações de gravação
    recording_enabled = models.BooleanField(default=True)
    recording_retention_days = models.IntegerField(default=30)  # 7, 15, 30 dias
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantAwareManager()

    @classmethod
    def get_resource_type(cls):
        return 'camera'

    def __str__(self):
        return self.name