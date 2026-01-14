from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    """Gestor customizado para criação de utilizadores e superusers."""
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("O email é obrigatório")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        return self.create_user(email, name, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo principal de utilizador do sistema."""
    ROLE_CHOICES = (
        ("admin", "Administrador"),
        ("viewer", "Visualizador"),
    )
    
    PLAN_CHOICES = (
        ("basic", "Basic - 7 dias"),
        ("pro", "Pro - 15 dias"),
        ("premium", "Premium - 30 dias"),
    )

    organization = models.ForeignKey('tenants.Organization', on_delete=models.CASCADE, related_name='users', null=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="viewer")
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="basic")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = UsuarioManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    @property
    def recording_days(self):
        """Retorna dias de gravação baseado no plano da organização"""
        if self.organization and hasattr(self.organization, 'subscription'):
            return self.organization.subscription.recording_days
        return {'basic': 7, 'pro': 15, 'premium': 30}.get(self.plan, 7)
    
    @property
    def max_cameras(self):
        """Retorna limite de câmeras por plano da organização"""
        if self.organization and hasattr(self.organization, 'subscription'):
            return self.organization.subscription.max_cameras
        return {'basic': 10, 'pro': 50, 'premium': 200}.get(self.plan, 10)
    
    @property
    def max_clips(self):
        """Retorna limite de clipes por plano da organização"""
        if self.organization and hasattr(self.organization, 'subscription'):
            return self.organization.subscription.max_clips
        return {'basic': 10, 'pro': 50, 'premium': 999999}.get(self.plan, 10)

    @property
    def max_concurrent_streams(self):
        """Retorna limite de streams simultâneos por plano da organização"""
        if self.organization and hasattr(self.organization, 'subscription'):
            return self.organization.subscription.max_concurrent_streams
        return {"basic": 4, "pro": 16, "premium": 64}.get(self.plan, 4)

    def __str__(self):
        return self.email