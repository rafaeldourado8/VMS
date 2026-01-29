from django.db import models
from django.conf import settings
from apps.cameras.models import Camera
import re

class LPRDetection(models.Model):
    """Detecções de placas LPR"""
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name="lpr_detections")
    plate_text = models.CharField(max_length=20, db_index=True)
    confidence = models.FloatField()
    bbox = models.JSONField()  # [x1, y1, x2, y2]
    plate_id = models.CharField(max_length=50)
    
    # Imagens
    plate_image_path = models.CharField(max_length=500)
    full_frame_path = models.CharField(max_length=500)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Validação Mercosul
    is_mercosul = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'camera']),
            models.Index(fields=['plate_text']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-detecta Mercosul (ABC1D23)
        if self.plate_text and len(self.plate_text) == 7:
            self.is_mercosul = bool(re.match(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$', self.plate_text))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.plate_text} - {self.camera.name} - {self.timestamp}"
