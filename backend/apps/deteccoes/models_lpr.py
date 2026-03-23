from django.db import models
from django.conf import settings
from apps.cameras.models import Camera
import django.utils.timezone
import re

VEHICLE_TYPE_CHOICES = (
    ("car", "Automovel"),
    ("motorcycle", "Motocicleta"),
    ("truck", "Caminhao"),
    ("bus", "Onibus"),
    ("van", "Van"),
    ("utility", "Utilitario"),
    ("unknown", "Desconhecido"),
)

class LPRDetection(models.Model):
    """Detecções de placas LPR via push de cameras Intelbras/Hikvision"""
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name="lpr_detections")
    plate_text = models.CharField(max_length=20, db_index=True)
    confidence = models.FloatField()
    bbox = models.JSONField(default=list, blank=True)  # [x1, y1, x2, y2]
    plate_id = models.CharField(max_length=50, blank=True, default="")

    # Imagens
    plate_image_path = models.CharField(max_length=500, blank=True, default="")
    full_frame_path = models.CharField(max_length=500, blank=True, default="")

    # Informacoes do veiculo (push Intelbras/Hikvision)
    vehicle_brand = models.CharField(max_length=50, blank=True, default="", help_text="Marca do veiculo (Toyota, Ford...)")
    vehicle_model = models.CharField(max_length=100, blank=True, default="", help_text="Modelo (Corolla, Ka...)")
    vehicle_color = models.CharField(max_length=30, blank=True, default="", help_text="Cor do veiculo")
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default="unknown")
    vehicle_year = models.IntegerField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, default="")
    direction = models.CharField(max_length=20, blank=True, default="", help_text="Direcao do veiculo")
    trigger_source = models.CharField(max_length=50, blank=True, default="", help_text="Fonte do disparo")

    # Metadata
    timestamp = models.DateTimeField(db_index=True, default=django.utils.timezone.now)
    metadata = models.JSONField(default=dict, blank=True)

    # Validação Mercosul
    is_mercosul = models.BooleanField(default=False)

    # Device info (push)
    device_id = models.CharField(max_length=100, blank=True, default="", help_text="ID do dispositivo que enviou")

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'camera']),
            models.Index(fields=['plate_text']),
            models.Index(fields=['vehicle_brand']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['camera', 'plate_text', 'timestamp'],
                name='unique_detection_per_camera',
            ),
        ]

    def save(self, *args, **kwargs):
        # Auto-detecta Mercosul (ABC1D23)
        if self.plate_text and len(self.plate_text) == 7:
            self.is_mercosul = bool(re.match(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$', self.plate_text.upper()))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plate_text} - {self.camera.name} - {self.timestamp}"
