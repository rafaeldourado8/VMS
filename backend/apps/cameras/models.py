from django.conf import settings
from django.db import models

STATUS_CHOICES = (("online", "Online"), ("offline", "Offline"))

class Camera(models.Model):
    """Modelo de persistência de Câmaras."""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cameras",
    )
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="online")
    stream_url = models.CharField(max_length=1000, unique=True)
    thumbnail_url = models.CharField(max_length=1000, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    detection_settings = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name