from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.cameras.models import Camera
from apps.notifications.services import NotificationService


@receiver(pre_save, sender=Camera)
def detect_camera_status_change(sender, instance, **kwargs):
    """Detecta mudança de status da câmera"""
    if instance.pk:  # Apenas para updates
        try:
            old_camera = Camera.objects.get(pk=instance.pk)
            
            # Se mudou de online para offline
            if old_camera.status == 'online' and instance.status == 'offline':
                # Enviar notificação após o save
                instance._send_offline_alert = True
        except Camera.DoesNotExist:
            pass


@receiver(post_save, sender=Camera)
def send_camera_offline_alert(sender, instance, created, **kwargs):
    """Envia alerta quando câmera fica offline"""
    if not created and getattr(instance, '_send_offline_alert', False):
        NotificationService.send_camera_offline_alert(instance)
        delattr(instance, '_send_offline_alert')
