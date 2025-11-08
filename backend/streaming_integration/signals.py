"""
Signals para sincronização automática com o serviço de streaming.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.apps import apps
from .services import StreamingService

logger = logging.getLogger(__name__)


def get_camera_model():
    """
    Obtém o modelo Camera dinamicamente.
    Adapta-se a diferentes nomes de app.
    """
    # Tente encontrar o modelo Camera em diferentes apps
    possible_apps = ['cameras', 'camera', 'core', 'main', 'api']
    
    for app_name in possible_apps:
        try:
            return apps.get_model(app_name, 'Camera')
        except LookupError:
            continue
    
    logger.warning("Modelo Camera não encontrado. Signals não serão registrados.")
    return None


# Obter modelo dinamicamente
Camera = get_camera_model()


if Camera:
    @receiver(post_save, sender=Camera)
    def camera_post_save_handler(sender, instance, created, **kwargs):
        """
        Signal executado após salvar uma câmera.
        """
        # Verificar se a câmera está ativa
        is_active = getattr(instance, 'is_active', True) or getattr(instance, 'active', True)
        
        if created and is_active:
            # Criar stream para nova câmera
            logger.info(f"Criando stream para nova câmera {instance.id}")
            StreamingService.create_stream_for_camera(instance)
            
        elif not created and hasattr(instance, 'stream_id') and instance.stream_id:
            # Atualizar stream existente
            logger.info(f"Atualizando stream para câmera {instance.id}")
            StreamingService.update_stream_for_camera(instance)


    @receiver(post_delete, sender=Camera)
    def camera_post_delete_handler(sender, instance, **kwargs):
        """
        Signal executado após deletar uma câmera.
        """
        logger.info(f"Deletando stream para câmera {instance.id}")
        StreamingService.delete_stream_for_camera(instance)