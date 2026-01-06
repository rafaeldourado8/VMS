from django.db import models


class SectorModel(models.Model):
    """Modelo de persistência para Setor"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sectors'
        verbose_name = 'Setor'
        verbose_name_plural = 'Setores'

    def __str__(self):
        return self.name


class AuditLogModel(models.Model):
    """Log de auditoria imutável (LGPD Art. 37)"""
    user = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT)
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)

    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"
