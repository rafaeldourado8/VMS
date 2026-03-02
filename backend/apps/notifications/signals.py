from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import LoginLog


def get_client_ip(request):
    """Obtém IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Registra login e envia email de notificação"""
    
    # Criar log de login
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    login_log = LoginLog.objects.create(
        user=user,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Enviar email de notificação
    try:
        admin_emails = settings.ADMIN_NOTIFICATION_EMAILS if hasattr(settings, 'ADMIN_NOTIFICATION_EMAILS') else []
        
        if admin_emails:
            send_mail(
                subject=f'[GT-Vision] Login: {user.email}',
                message=f'''
Novo login detectado:

Usuário: {user.name} ({user.email})
Data/Hora: {login_log.logged_in_at.strftime('%d/%m/%Y %H:%M:%S')}
IP: {ip_address or 'N/A'}
User Agent: {user_agent[:100] if user_agent else 'N/A'}
                '''.strip(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=True,
            )
    except Exception as e:
        # Log error mas não falha o login
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao enviar email de login: {e}')
