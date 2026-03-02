from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class LoginLog(models.Model):
    """Log de logins no sistema"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_logs',
        verbose_name='Usuário'
    )
    
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP')
    user_agent = models.TextField(null=True, blank=True, verbose_name='User Agent')
    
    logged_in_at = models.DateTimeField(auto_now_add=True, verbose_name='Login em')
    
    class Meta:
        db_table = 'login_logs'
        verbose_name = 'Log de Login'
        verbose_name_plural = 'Logs de Login'
        ordering = ['-logged_in_at']
        indexes = [
            models.Index(fields=['user', '-logged_in_at']),
        ]
    
    def __str__(self):
        return f'{self.user.email} - {self.logged_in_at}'


class NotificationPreference(models.Model):
    """Preferências de notificação por usuário"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        verbose_name='Usuário'
    )
    
    # Email
    email_alerts = models.BooleanField(default=True, verbose_name='Alertas por Email')
    
    # Push
    push_notifications = models.BooleanField(default=False, verbose_name='Notificações Push')
    
    # Câmera Offline
    camera_offline = models.BooleanField(default=True, verbose_name='Alertas de Câmera Offline')
    
    # Sistema
    system_alerts = models.BooleanField(default=True, verbose_name='Alertas do Sistema')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Preferência de Notificação'
        verbose_name_plural = 'Preferências de Notificação'
    
    def __str__(self):
        return f'Preferências de {self.user.email}'


class NotificationLog(models.Model):
    """Log de notificações enviadas"""
    
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('push', 'Push'),
        ('sms', 'SMS'),
    ]
    
    CATEGORY_CHOICES = [
        ('camera_offline', 'Câmera Offline'),
        ('system', 'Sistema'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Usuário'
    )
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Tipo')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='Categoria')
    
    title = models.CharField(max_length=255, verbose_name='Título')
    message = models.TextField(verbose_name='Mensagem')
    
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Enviado em')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Lido em')
    
    success = models.BooleanField(default=True, verbose_name='Sucesso')
    error_message = models.TextField(null=True, blank=True, verbose_name='Mensagem de Erro')
    
    class Meta:
        db_table = 'notification_logs'
        verbose_name = 'Log de Notificação'
        verbose_name_plural = 'Logs de Notificações'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['user', '-sent_at']),
            models.Index(fields=['category', '-sent_at']),
        ]
    
    def __str__(self):
        return f'{self.get_type_display()} - {self.title}'
