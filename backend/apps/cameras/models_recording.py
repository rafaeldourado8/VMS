from django.db import models
from django.utils import timezone

class Recording(models.Model):
    """Gravação de vídeo com snapshot em cache."""
    camera = models.ForeignKey("cameras.Camera", on_delete=models.CASCADE, related_name="recordings")
    
    # Arquivo de vídeo
    video_path = models.CharField(max_length=500, help_text="Caminho: /recordings/cam_X/YYYY-MM-DD_HH-MM-SS.mp4")
    duration_seconds = models.IntegerField(default=0)
    file_size_bytes = models.BigIntegerField(default=0)
    
    # Snapshot em cache (foto estática da capa)
    snapshot_cached = models.ImageField(upload_to="recording_snapshots/%Y/%m/%d/", null=True, blank=True)
    
    # Timestamps
    started_at = models.DateTimeField(db_index=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["camera", "-started_at"])
        ]

    def __str__(self):
        return f"Recording {self.camera.name} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"
