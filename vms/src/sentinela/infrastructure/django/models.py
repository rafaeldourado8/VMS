from django.db import models
import uuid

class VehicleSearchModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    city_id = models.UUIDField()
    user_id = models.UUIDField()
    plate = models.CharField(max_length=20, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    vehicle_type = models.CharField(max_length=50, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'vehicle_searches'
        verbose_name = 'Vehicle Search'
        verbose_name_plural = 'Vehicle Searches'
        indexes = [
            models.Index(fields=['city_id']),
            models.Index(fields=['user_id']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at'])
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        criteria = []
        if self.plate:
            criteria.append(f"Plate: {self.plate}")
        if self.color:
            criteria.append(f"Color: {self.color}")
        if self.vehicle_type:
            criteria.append(f"Type: {self.vehicle_type}")
        return f"Search {self.id} - {', '.join(criteria)}"
    
    def to_entity(self):
        from domain.entities.vehicle_search import VehicleSearch
        return VehicleSearch(
            id=str(self.id),
            city_id=str(self.city_id),
            user_id=str(self.user_id),
            plate=self.plate,
            color=self.color,
            vehicle_type=self.vehicle_type,
            start_date=self.start_date,
            end_date=self.end_date,
            status=self.status,
            created_at=self.created_at,
            error_message=self.error_message
        )
    
    @staticmethod
    def from_entity(search):
        return VehicleSearchModel(
            id=search.id,
            city_id=search.city_id,
            user_id=search.user_id,
            plate=search.plate,
            color=search.color,
            vehicle_type=search.vehicle_type,
            start_date=search.start_date,
            end_date=search.end_date,
            status=search.status,
            error_message=search.error_message
        )
