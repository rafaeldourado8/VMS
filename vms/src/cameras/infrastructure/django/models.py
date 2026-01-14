from django.db import models
import uuid

class CameraModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    stream_url = models.URLField(max_length=500)
    type = models.CharField(max_length=10, choices=[
        ('rtsp', 'RTSP (LPR)'),
        ('rtmp', 'RTMP (Bullet)')
    ])
    lpr_enabled = models.BooleanField(default=False)
    city_id = models.UUIDField()
    status = models.CharField(max_length=20, default='inactive', choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cameras'
        verbose_name = 'Camera'
        verbose_name_plural = 'Cameras'
        indexes = [
            models.Index(fields=['city_id']),
            models.Index(fields=['type']),
            models.Index(fields=['status']),
            models.Index(fields=['lpr_enabled'])
        ]
    
    def __str__(self):
        lpr_status = ' [LPR]' if self.lpr_enabled else ''
        return f"{self.name} ({self.type}){lpr_status}"
    
    def to_entity(self):
        from domain.entities.camera import Camera
        camera = Camera(
            id=str(self.id),
            name=self.name,
            stream_url=self.stream_url,
            city_id=str(self.city_id),
            type=self.type,
            status=self.status
        )
        camera.lpr_enabled = self.lpr_enabled
        return camera
    
    @staticmethod
    def from_entity(camera):
        return CameraModel(
            id=camera.id,
            name=camera.name,
            stream_url=camera.stream_url,
            type=camera.type,
            lpr_enabled=camera.lpr_enabled,
            city_id=camera.city_id,
            status=camera.status
        )
