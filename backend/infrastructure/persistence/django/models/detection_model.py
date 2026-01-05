from django.db import models

VEHICLE_TYPE_CHOICES = (
    ("car", "Carro"),
    ("motorcycle", "Motocicleta"),
    ("truck", "Caminhão"),
    ("bus", "Ônibus"),
    ("unknown", "Desconhecido"),
)

class DetectionModel(models.Model):
    """Modelo Django para persistência de Detecções"""
    
    camera = models.ForeignKey(
        "camera_model.CameraModel",
        on_delete=models.CASCADE,
        related_name="detections",
    )
    plate = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    confidence = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(db_index=True)
    vehicle_type = models.CharField(
        max_length=20, 
        choices=VEHICLE_TYPE_CHOICES, 
        default="unknown"
    )
    image_url = models.CharField(max_length=1000, blank=True, null=True)
    video_url = models.CharField(max_length=1000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'deteccoes_deteccao'
        ordering = ["-timestamp"]
        indexes = [models.Index(fields=["camera", "-timestamp"])]
        
    def __str__(self):
        plate_display = self.plate or "N/A"
        return f"Detecção ({plate_display})"
