from django.db import models
import uuid

class CityModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=50)
    plan = models.CharField(max_length=20, choices=[
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('premium', 'Premium')
    ])
    max_cameras = models.IntegerField(default=1000)
    max_lpr_cameras = models.IntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cities'
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
    
    def __str__(self):
        return f"{self.name} ({self.plan})"
    
    def to_entity(self):
        from domain.entities.city import City
        return City(
            id=str(self.id),
            name=self.name,
            slug=self.slug,
            plan=self.plan,
            max_cameras=self.max_cameras,
            max_lpr_cameras=self.max_lpr_cameras
        )
    
    @staticmethod
    def from_entity(city):
        return CityModel(
            id=city.id,
            name=city.name,
            slug=city.slug,
            plan=city.plan,
            max_cameras=city.max_cameras,
            max_lpr_cameras=city.max_lpr_cameras
        )
