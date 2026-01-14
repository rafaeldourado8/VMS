from django.db import models
import uuid

class DetectionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    camera_id = models.UUIDField()
    plate = models.CharField(max_length=20)
    confidence = models.FloatField()
    image_url = models.URLField(max_length=500)
    detected_at = models.DateTimeField()
    city_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'detections'
        verbose_name = 'Detection'
        verbose_name_plural = 'Detections'
        indexes = [
            models.Index(fields=['camera_id']),
            models.Index(fields=['plate']),
            models.Index(fields=['city_id']),
            models.Index(fields=['detected_at'])
        ]
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"{self.plate} - {self.confidence:.2%}"
    
    def to_entity(self):
        from domain.entities.detection import Detection
        return Detection(
            id=str(self.id),
            camera_id=str(self.camera_id),
            plate=self.plate,
            confidence=self.confidence,
            image_url=self.image_url,
            detected_at=self.detected_at,
            city_id=str(self.city_id)
        )
    
    @staticmethod
    def from_entity(detection):
        return DetectionModel(
            id=detection.id,
            camera_id=detection.camera_id,
            plate=detection.plate,
            confidence=detection.confidence,
            image_url=detection.image_url,
            detected_at=detection.detected_at,
            city_id=detection.city_id
        )
