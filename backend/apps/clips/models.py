from django.db import models
from django.conf import settings

class Clip(models.Model):
    """Modelo para clips de vídeo recortados"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clips"
    )
    camera = models.ForeignKey(
        "cameras.Camera",
        on_delete=models.SET_NULL,  # Não deleta clip se câmera for excluída
        related_name="clips",
        null=True,
        blank=True
    )
    camera_id_backup = models.IntegerField(help_text="ID da câmera para referência histórica")
    camera_name_backup = models.CharField(max_length=255, help_text="Nome da câmera no momento da criação")
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    file_path = models.CharField(max_length=1000)
    thumbnail_path = models.CharField(max_length=1000, blank=True, null=True)
    duration_seconds = models.IntegerField()
    file_size_bytes = models.BigIntegerField(default=0)
    external_id = models.CharField(max_length=64, blank=True, null=True, unique=True)
    status = models.CharField(max_length=20, default='pending')
    is_protected = models.BooleanField(default=True, help_text="Protegido contra retenção automática")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'created_at']),
            models.Index(fields=['external_id']),
            models.Index(fields=['is_protected']),
        ]

    def __str__(self):
        return f"{self.name} - {self.camera_name_backup}"