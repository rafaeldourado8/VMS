"""
Configuração da app de integração com streaming.
"""

from django.apps import AppConfig


class StreamingIntegrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'streaming_integration'
    verbose_name = 'Integração com Streaming'
    
    def ready(self):
        """Importa signals quando a app está pronta."""
        import streaming_integration.signals  # noqa