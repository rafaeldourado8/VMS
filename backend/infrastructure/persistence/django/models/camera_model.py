from django.conf import settings
from django.db import models

STATUS_CHOICES = (("online", "Online"), ("offline", "Offline"))

class CameraModel(models.Model):
    """Modelo Django para persistência de Câmeras"""
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cameras",
    )
    sector = models.ForeignKey(
        'SectorModel',
        on_delete=models.PROTECT,
        related_name='cameras',
        null=True
    )
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="online")
    stream_url = models.CharField(max_length=1000, unique=True)
    thumbnail_url = models.CharField(max_length=1000, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    ai_enabled = models.BooleanField(default=False)
    recording_enabled = models.BooleanField(default=True)
    recording_retention_days = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cameras_camera'
        
    def __str__(self):
        return self.name
