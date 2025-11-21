# VMS/backend/streaming_integration/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.cameras.models import Camera
import logging

# Importar as tasks em vez do cliente direto
from .tasks import sync_camera_mediamtx, remove_camera_mediamtx

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Camera)
def on_camera_save(sender, instance: Camera, created, **kwargs):
    try:
        camera_id = str(instance.id)
        rtsp_url = instance.stream_url
        
        if not rtsp_url:
            return
            
        # Usar .delay() ou .apply_async() para enviar para o Celery
        logger.info(f"Agendando configuração da câmera {camera_id} para o Worker...")
        sync_camera_mediamtx.delay(camera_id, rtsp_url)
        
    except Exception as e:
        logger.error(f"Erro ao agendar task post_save: {e}", exc_info=True)

@receiver(post_delete, sender=Camera)
def on_camera_delete(sender, instance: Camera, **kwargs):
    try:
        camera_id = str(instance.id)
        
        logger.info(f"Agendando remoção da câmera {camera_id}...")
        remove_camera_mediamtx.delay(camera_id)
        
    except Exception as e:
        logger.error(f"Erro ao agendar task post_delete: {e}", exc_info=True)