"""
Helper para enviar alertas do sistema manualmente
Uso:
    from apps.notifications.alerts import send_alert
    send_alert('Serviço X falhou', 'Detalhes do erro...')
"""
from apps.notifications.services import NotificationService


def send_alert(title, message):
    """Envia alerta do sistema para todos os admins"""
    return NotificationService.send_system_alert(title, message)


def send_service_down_alert(service_name):
    """Alerta de serviço fora do ar"""
    return send_alert(
        title=f'Serviço Offline: {service_name}',
        message=f'O serviço {service_name} está fora do ar. Verifique a conexão.'
    )


def send_database_error_alert(error):
    """Alerta de erro no banco de dados"""
    return send_alert(
        title='Erro no Banco de Dados',
        message=f'Erro detectado no banco de dados:\n\n{str(error)}'
    )


def send_api_error_alert(endpoint, error):
    """Alerta de erro em API externa"""
    return send_alert(
        title=f'Erro na API: {endpoint}',
        message=f'Falha ao comunicar com {endpoint}:\n\n{str(error)}'
    )
