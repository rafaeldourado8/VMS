from django.db import models
from apps.usuarios.models import Usuario

class IAMPermission(models.Model):
    """Permissões granulares do sistema"""
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    resource = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

class IAMRule(models.Model):
    """Regras de acesso baseadas em condições"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    conditions = models.JSONField(default=dict)
    actions = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UserPermissions(models.Model):
    """Permissões atribuídas a usuários"""
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='iam_permissions')
    permissions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {len(self.permissions)} permissions"

class TenantIsolation(models.Model):
    """Isolamento de dados por usuário/tenant"""
    user = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tenant_data')
    resource_type = models.CharField(max_length=50)  # camera, recording, detection, etc
    resource_id = models.IntegerField()
    can_read = models.BooleanField(default=True)
    can_write = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'resource_type', 'resource_id']
        indexes = [
            models.Index(fields=['user', 'resource_type']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.resource_type}:{self.resource_id}"
