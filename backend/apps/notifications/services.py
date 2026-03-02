from django.core.mail import send_mail
from django.conf import settings
from .models import NotificationPreference, NotificationLog


class NotificationService:
    """Serviço para envio de notificações"""
    
    @staticmethod
    def get_or_create_preferences(user):
        """Obtém ou cria preferências do usuário"""
        prefs, created = NotificationPreference.objects.get_or_create(user=user)
        return prefs
    
    @staticmethod
    def send_email_notification(user, category, title, message):
        """Envia notificação por email"""
        prefs = NotificationService.get_or_create_preferences(user)
        
        # Verifica se o usuário quer receber este tipo de notificação
        if not prefs.email_alerts:
            return False
        
        # Verifica categoria específica
        category_enabled = {
            'camera_offline': prefs.camera_offline,
            'system': prefs.system_alerts,
        }
        
        if not category_enabled.get(category, True):
            return False
        
        try:
            send_mail(
                subject=f'[GT-Vision] {title}',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            
            NotificationLog.objects.create(
                user=user,
                type='email',
                category=category,
                title=title,
                message=message,
                success=True
            )
            return True
            
        except Exception as e:
            NotificationLog.objects.create(
                user=user,
                type='email',
                category=category,
                title=title,
                message=message,
                success=False,
                error_message=str(e)
            )
            return False
    
    @staticmethod
    def send_camera_offline_alert(camera, users=None):
        """Envia alerta de câmera offline"""
        from apps.usuarios.models import Usuario
        
        if users is None:
            users = Usuario.objects.filter(is_active=True)
        
        title = f'Câmera Offline: {camera.name}'
        message = f'''A câmera {camera.name} está offline.

Localização: {camera.location}
Última atualização: {camera.updated_at.strftime('%d/%m/%Y %H:%M:%S')}

Verifique a conexão da câmera.'''
        
        sent_count = 0
        for user in users:
            if NotificationService.send_email_notification(
                user=user,
                category='camera_offline',
                title=title,
                message=message
            ):
                sent_count += 1
        
        return sent_count
    def send_system_alert(title, message, users=None):
        """Envia alerta genérico do sistema"""
        from apps.usuarios.models import Usuario
        
        if users is None:
            users = Usuario.objects.filter(is_active=True)
        
        sent_count = 0
        for user in users:
            if NotificationService.send_email_notification(
                user=user,
                category='system',
                title=title,
                message=message
            ):
                sent_count += 1
        
        return sent_count
