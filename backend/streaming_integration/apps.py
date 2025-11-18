from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class StreamingIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'streaming_integration'

    def ready(self):
        # Importa os sinais para que sejam registados
        try:
            import streaming_integration.signals
            logger.info("Sinais de integração de streaming carregados.")
        except ImportError:
            pass