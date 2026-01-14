from django.db import models
from django.contrib.postgres.fields import ArrayField


class UserModel(models.Model):
    """Model Django para User."""
    
    id = models.CharField(max_length=36, primary_key=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password_hash = models.CharField(max_length=64)
    city_ids = ArrayField(models.CharField(max_length=36), default=list, blank=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.email
