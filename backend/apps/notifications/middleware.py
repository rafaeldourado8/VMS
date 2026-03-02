import logging
from django.utils.deprecation import MiddlewareMixin
from apps.notifications.services import NotificationService

logger = logging.getLogger(__name__)


class SystemAlertMiddleware(MiddlewareMixin):
    """Middleware para capturar erros críticos e enviar alertas"""
    
    def process_exception(self, request, exception):
        """Captura exceções não tratadas"""
        
        # Ignorar erros comuns (404, 403, etc)
        if hasattr(exception, 'status_code'):
            if exception.status_code in [400, 401, 403, 404]:
                return None
        
        # Log do erro
        logger.error(f"System Error: {exception}", exc_info=True)
        
        # Enviar alerta apenas para erros críticos
        error_type = type(exception).__name__
        critical_errors = [
            'DatabaseError',
            'OperationalError',
            'ConnectionError',
            'TimeoutError',
            'MemoryError',
        ]
        
        if error_type in critical_errors:
            try:
                NotificationService.send_system_alert(
                    title=f'Erro Crítico: {error_type}',
                    message=f'''Erro detectado no sistema:

Tipo: {error_type}
Mensagem: {str(exception)}
Path: {request.path}
Método: {request.method}

Verifique os logs para mais detalhes.'''
                )
            except Exception as e:
                logger.error(f"Falha ao enviar alerta: {e}")
        
        return None
