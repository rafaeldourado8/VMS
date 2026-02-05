from django.db import models

class Recording(models.Model):
    camera_id = models.IntegerField(db_index=True)
    date = models.DateField(db_index=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=512)
    size_mb = models.FloatField(default=0)
    duration_min = models.FloatField(default=0)
    codec = models.CharField(max_length=50, default='h264')
    is_valid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recordings'
        unique_together = ['camera_id', 'date', 'file_name']
        ordering = ['-date', 'file_name']
