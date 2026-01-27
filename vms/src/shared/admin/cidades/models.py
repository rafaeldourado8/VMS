import uuid
from django.db import models
from .enums import CityStatus, Plan

class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=CityStatus.choices, default=CityStatus.ACTIVE)
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.BASIC)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cities'
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def is_active(self):
        return self.status == CityStatus.ACTIVE
