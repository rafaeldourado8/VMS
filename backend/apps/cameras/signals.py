import logging
import requests
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.cameras.models import Camera

logger = logging.getLogger(__name__)

AI_DETECTION_URL = "http://ai_detection:5000"

@receiver(post_save, sender=Camera)
def handle_camera_save(sender, instance, created, **kwargs):
    """
    Inicia/para detecção AI quando câmera é criada ou atualizada
    """
    try:
        if instance.ai_enabled:
            # Inicia detecção - NÃO passa source_url, deixa AI Detection buscar do MediaMTX
            response = requests.post(
                f"{AI_DETECTION_URL}/cameras/{instance.id}/start",
                json={},  # Vazio - AI Detection vai buscar do MediaMTX
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"AI detection started for camera {instance.id}")
            else:
                logger.error(f"Failed to start AI detection for camera {instance.id}: {response.text}")
        else:
            # Para detecção
            response = requests.post(
                f"{AI_DETECTION_URL}/cameras/{instance.id}/stop",
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"AI detection stopped for camera {instance.id}")
            else:
                logger.warning(f"Failed to stop AI detection for camera {instance.id}: {response.text}")
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with AI detection service: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in camera signal: {e}")


@receiver(post_delete, sender=Camera)
def handle_camera_delete(sender, instance, **kwargs):
    """
    Para detecção AI quando câmera é deletada
    """
    try:
        response = requests.post(
            f"{AI_DETECTION_URL}/cameras/{instance.id}/stop",
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"AI detection stopped for deleted camera {instance.id}")
        else:
            logger.warning(f"Failed to stop AI detection for deleted camera {instance.id}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with AI detection service: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in camera delete signal: {e}")
