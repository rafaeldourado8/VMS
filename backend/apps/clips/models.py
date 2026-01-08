from django.conf import settings
from django.db import models

class Clip(models.Model):
    """Modelo para clips de vídeo recortados"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clips"
    )
    camera = models.ForeignKey(
        "cameras.Camera",
        on_delete=models.CASCADE,
        related_name="clips"
    )
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    file_path = models.CharField(max_length=1000)
    thumbnail_path = models.CharField(max_length=1000, blank=True, null=True)
    duration_seconds = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.camera.name}"

class Mosaico(models.Model):
    """Modelo para mosaicos de câmeras"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mosaicos"
    )
    name = models.CharField(max_length=255)
    cameras = models.ManyToManyField(
        "cameras.Camera",
        through="MosaicoCameraPosition",
        related_name="mosaicos"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class MosaicoCameraPosition(models.Model):
    """Posição das câmeras no mosaico (máximo 4)"""
    mosaico = models.ForeignKey(Mosaico, on_delete=models.CASCADE)
    camera = models.ForeignKey("cameras.Camera", on_delete=models.CASCADE)
    position = models.IntegerField(choices=[(1, 'Posição 1'), (2, 'Posição 2'), (3, 'Posição 3'), (4, 'Posição 4')])

    class Meta:
        unique_together = [['mosaico', 'position'], ['mosaico', 'camera']]