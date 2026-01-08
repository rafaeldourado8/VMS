from django.db import models

VEHICLE_TYPE_CHOICES = (
    ("car", "Carro"),
    ("motorcycle", "Motocicleta"),
    ("truck", "Caminhão"),
    ("bus", "Ônibus"),
    ("unknown", "Desconhecido"),
)

class Deteccao(models.Model):
    """Modelo para armazenamento de detecções de veículos e matrículas."""
    
    camera = models.ForeignKey(
        "cameras.Camera",
        on_delete=models.CASCADE,
        related_name="deteccoes",
        help_text="A câmara que originou esta detecção."
    )

    # Campos de dados da detecção
    plate = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    confidence = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(db_index=True)
    vehicle_type = models.CharField(
        max_length=20, 
        choices=VEHICLE_TYPE_CHOICES, 
        default="unknown"
    )

    # URLs para evidências multimédia
    image_url = models.CharField(max_length=1000, blank=True, null=True)
    video_url = models.CharField(max_length=1000, blank=True, null=True)

    # Controlo interno
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Detecção"
        verbose_name_plural = "Detecções"
        # Índice composto para otimizar filtros por câmara + tempo
        indexes = [models.Index(fields=["camera", "-timestamp"])]

    def __str__(self):
        plate_display = self.plate or "N/A"
        return f"Detecção ({plate_display}) em {self.camera.name}"