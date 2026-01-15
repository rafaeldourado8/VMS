from django.db import models
from django.utils import timezone

class Organization(models.Model):
    """Organização (cidade/empresa) - cada uma tem seu próprio banco"""
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    database_name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True, help_text="Email principal da prefeitura")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

class Subscription(models.Model):
    """Plano de assinatura com dias de gravação"""
    PLAN_CHOICES = (
        ('basic', 'Basic - 7 dias'),
        ('pro', 'Pro - 15 dias'),
        ('premium', 'Premium - 30 dias'),
    )
    
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    recording_days = models.IntegerField(default=7)
    max_cameras = models.IntegerField(default=10)
    max_users = models.IntegerField(default=3)
    max_clips = models.IntegerField(default=10)
    max_concurrent_streams = models.IntegerField(default=4)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.organization.name} - {self.plan}"
    
    def save(self, *args, **kwargs):
        # Auto-set limits based on plan
        limits = {
            'basic': {'recording_days': 7, 'max_cameras': 10, 'max_users': 3, 'max_clips': 10, 'max_concurrent_streams': 4},
            'pro': {'recording_days': 15, 'max_cameras': 50, 'max_users': 5, 'max_clips': 50, 'max_concurrent_streams': 16},
            'premium': {'recording_days': 30, 'max_cameras': 200, 'max_users': 10, 'max_clips': 999999, 'max_concurrent_streams': 64},
        }
        plan_limits = limits.get(self.plan, limits['basic'])
        for key, value in plan_limits.items():
            setattr(self, key, value)
        super().save(*args, **kwargs)
