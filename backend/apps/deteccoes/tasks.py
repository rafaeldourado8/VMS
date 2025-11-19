import logging
import json
from celery import shared_task
from .domain import DetectionProcessor

logger = logging.getLogger(__name__)

@shared_task(name="process_detection_message")
def process_detection_message(message_body: str):
    """
    Interface assíncrona (Adapter) entre RabbitMQ e o Domínio.
    Apenas orquestra a chamada, não contém regra de negócio.
    """
    try:
        data = json.loads(message_body)
        logger.info(f"Mensagem recebida na fila. Camera ID: {data.get('camera_id')}")

        # Instancia o processador de domínio
        processor = DetectionProcessor()
        
        # Delega o processamento real
        processor.process_raw_data(data)

    except json.JSONDecodeError:
        logger.error(f"Falha ao decodificar JSON da mensagem: {message_body}")
    except ValueError as e:
        logger.warning(f"Processamento interrompido: {str(e)}")
    except Exception as e:
        logger.error(f"Erro crítico inesperado na task: {str(e)}", exc_info=True)
