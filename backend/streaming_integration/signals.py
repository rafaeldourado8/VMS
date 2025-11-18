# VMS/backend/streaming_integration/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.cameras.models import Camera # Importa o seu modelo de Câmara
import logging

# Importa o novo cliente que acabámos de criar
from .client import mediamtx_api_client 

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Camera)
def on_camera_save(sender, instance: Camera, created, **kwargs):
    """
    Chamado sempre que uma câmara é CRIADA ou ATUALIZADA.
    """
    try:
        # 'instance' é o objeto Camera que foi guardado
        camera_id = str(instance.id)
        rtsp_url = instance.stream_url # Assumindo que o campo se chama 'stream_url'
        
        if not rtsp_url:
            logger.warning(f"Câmara {camera_id} guardada sem stream_url. A ignorar MediaMTX.")
            return
            
        logger.info(f"Sinal post_save detetado para a Câmara {camera_id}. A atualizar MediaMTX...")
        mediamtx_api_client.add_or_update_camera(camera_id, rtsp_url)
        
    except Exception as e:
        logger.error(f"Erro no sinal post_save da Câmara {instance.id}: {e}", exc_info=True)


@receiver(post_delete, sender=Camera)
def on_camera_delete(sender, instance: Camera, **kwargs):
    """
    Chamado sempre que uma câmara é ELIMINADA.
    """
    try:
        camera_id = str(instance.id)
        
        logger.info(f"Sinal post_delete detetado para a Câmara {camera_id}. A remover do MediaMTX...")
        mediamtx_api_client.remove_camera(camera_id)
        
    except Exception as e:
        logger.error(f"Erro no sinal post_delete da Câmara {instance.id}: {e}", exc_info=True)