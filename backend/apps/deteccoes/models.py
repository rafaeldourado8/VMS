from django.db import models
from django.utils import timezone

VEHICLE_TYPE_CHOICES = (
    ("car", "Carro"),
    ("motorcycle", "Motocicleta"),
    ("truck", "Caminhão"),
    ("bus", "Ônibus"),
    ("unknown", "Desconhecido"),
)

class Deteccao(models.Model):
    """Modelo para armazenamento de detecções OCR de placas."""
    
    camera = models.ForeignKey(
        "cameras.Camera",
        on_delete=models.CASCADE,
        related_name="deteccoes",
        help_text="Câmera que originou esta detecção."
    )

    # Dados OCR
    placa = models.CharField(max_length=20, db_index=True, help_text="Texto da placa detectada")
    confianca = models.FloatField(default=0.0, help_text="Confiança do OCR (0.0 a 1.0)")
    
    # Snapshot
    snapshot_path = models.CharField(
        max_length=500, 
        help_text="Caminho relativo: media/snapshots/YYYY/MM/DD/filename.jpg"
    )
    
    # Metadados
    vehicle_type = models.CharField(
        max_length=20, 
        choices=VEHICLE_TYPE_CHOICES, 
        default="unknown"
    )
    data_hora = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-data_hora"]
        verbose_name = "Detecção"
        verbose_name_plural = "Detecções"
        indexes = [
            models.Index(fields=["camera", "-data_hora"]),
            models.Index(fields=["placa", "-data_hora"])
        ]

    def __str__(self):
        return f"{self.placa} - Cam {self.camera.name} ({self.data_hora.strftime('%d/%m/%Y %H:%M')})"
    
    @property
    def snapshot_url(self):
        """Retorna URL completa do snapshot."""
        from django.conf import settings
        return f"{settings.MEDIA_URL}{self.snapshot_path}"