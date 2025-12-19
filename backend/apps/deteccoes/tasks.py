import logging
import json
from celery import shared_task
from .services import DeteccaoService
from .schemas import IngestDeteccaoDTO

logger = logging.getLogger(__name__)

@shared_task(name="process_detection_message")
def process_detection_message(message_body: str):
    """Task assíncrona para processar detecções da fila RabbitMQ."""
    try:
        data = json.loads(message_body)
        # O DTO garante a estrutura antes de enviar ao serviço
        dto = IngestDeteccaoDTO(**data)
        DeteccaoService.process_ingestion(dto)
    except Exception as e:
        logger.error(f"Erro no processamento assíncrono da detecção: {str(e)}")