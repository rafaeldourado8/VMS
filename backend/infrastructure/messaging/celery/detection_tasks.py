import json
import logging

from celery import shared_task
from infrastructure.persistence.django.repositories import DjangoDetectionRepository

from application.detection.commands.process_detection_command import ProcessDetectionCommand
from application.detection.handlers import ProcessDetectionHandler

logger = logging.getLogger(__name__)

@shared_task(name="process_detection_message")
def process_detection_message(message_body: str):
    """Task assíncrona para processar detecções da fila RabbitMQ usando DDD."""
    try:
        data = json.loads(message_body)
        
        # Usar handler DDD
        detection_repo = DjangoDetectionRepository()
        handler = ProcessDetectionHandler(detection_repo)
        
        command = ProcessDetectionCommand(**data)
        handler.handle(command)
        
        logger.info(f"Detecção processada com sucesso: camera_id={data.get('camera_id')}")
        
    except Exception as e:
        logger.error(f"Erro no processamento assíncrono da detecção: {str(e)}")
        raise

@shared_task(name="cleanup_old_detections")
def cleanup_old_detections(days: int = 30):
    """Task para limpeza de detecções antigas."""
    try:
        from datetime import datetime, timedelta
        from apps.deteccoes.models import Deteccao
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = Deteccao.objects.filter(created_at__lt=cutoff_date).delete()[0]
        
        logger.info(f"Limpeza concluída: {deleted_count} detecções removidas")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Erro na limpeza de detecções: {str(e)}")
        raise