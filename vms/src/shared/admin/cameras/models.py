import uuid
from django.db import models
from shared.admin.cidades.models import City
from .enums import CameraProtocol

class Camera(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    public_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, db_index=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='cameras')
    
    name = models.CharField(max_length=255)
    stream_url = models.CharField(max_length=512)
    protocol = models.CharField(max_length=10, choices=CameraProtocol.choices)
    
    is_lpr = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    recording_enabled = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cameras'
        verbose_name = 'Câmera'
        verbose_name_plural = 'Câmeras'
        ordering = ['-created_at']
        unique_together = [['city', 'name']]
        indexes = [
            models.Index(fields=['city', 'is_active']),
            models.Index(fields=['public_id']),
        ]
        permissions = [
            ('view_city_cameras', 'Can view cameras from own city'),
            ('manage_city_cameras', 'Can manage cameras from own city'),
        ]

    def __str__(self):
        return f"{self.name} ({self.city.name})"
