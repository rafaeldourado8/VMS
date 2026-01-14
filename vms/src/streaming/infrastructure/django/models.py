from django.db import models
import uuid

class StreamModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    camera_id = models.UUIDField(unique=True)
    hls_url = models.URLField(max_length=500)
    status = models.CharField(max_length=20, default='stopped', choices=[
        ('active', 'Active'),
        ('stopped', 'Stopped'),
        ('error', 'Error')
    ])
    started_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'streams'
        verbose_name = 'Stream'
        verbose_name_plural = 'Streams'
        indexes = [
            models.Index(fields=['camera_id']),
            models.Index(fields=['status'])
        ]
    
    def __str__(self):
        return f"Stream {self.camera_id} ({self.status})"
    
    def to_entity(self):
        from domain.entities.stream import Stream
        return Stream(
            id=str(self.id),
            camera_id=str(self.camera_id),
            hls_url=self.hls_url,
            status=self.status,
            started_at=self.started_at
        )
    
    @staticmethod
    def from_entity(stream):
        return StreamModel(
            id=stream.id,
            camera_id=stream.camera_id,
            hls_url=stream.hls_url,
            status=stream.status,
            started_at=stream.started_at
        )
