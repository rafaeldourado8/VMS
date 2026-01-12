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
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="online")
    stream_url = models.CharField(max_length=1000, unique=True)
    thumbnail_url = models.CharField(max_length=1000, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    detection_settings = models.JSONField(default=dict, blank=True, null=True)
    ai_enabled = models.BooleanField(default=False)
    roi_areas = models.JSONField(default=list, blank=True, null=True)
    virtual_lines = models.JSONField(default=list, blank=True, null=True)
    tripwires = models.JSONField(default=list, blank=True, null=True)
    zone_triggers = models.JSONField(default=list, blank=True, null=True)
    recording_enabled = models.BooleanField(default=True)
    recording_retention_days = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'name'],
                name='unique_camera_name_per_owner'
            )
        ]

    def __str__(self):
        return self.name

__all__ = ['Camera']
