import logging
import json
from celery import shared_task
from django.db import transaction
from .models import Deteccao
from apps.cameras.models import Camera
from .serializers import IngestDeteccaoSerializer

logger = logging.getLogger(__name__)

@shared_task(name="process_detection_message")
def process_detection_message(message_body: str):
    """
    Consome a mensagem da fila do RabbitMQ e a salva no banco de dados.
    Esta task é o "consumer".
    """
    try:
        data = json.loads(message_body)
        logger.info(f"Mensagem de detecção recebida para câmera: {data.get('camera_id')}")

        # Validação dos dados (usando o mesmo serializer da sua antiga IngestView)
        serializer = IngestDeteccaoSerializer(data=data)
        
        if not serializer.is_valid():
            logger.warning(f"Dados de detecção inválidos: {serializer.errors}. Mensagem: {message_body}")
            return # Descarta a mensagem

        validated_data = serializer.validated_data
        camera_id = validated_data.get('camera_id')
        
        try:
            # Busca a câmera no banco de dados
            camera_instance = Camera.objects.get(id=camera_id)
        except Camera.DoesNotExist:
            logger.error(f"Câmera com ID {camera_id} não encontrada. Descartando detecção.")
            return # Descarta a mensagem

        # Adiciona a instância da câmera aos dados para salvar
        validated_data['camera'] = camera_instance
        
        # Salva a detecção no banco de dados
        with transaction.atomic():
            Deteccao.objects.create(**validated_data)
            
        logger.info(f"Detecção da câmera {camera_id} salva com sucesso.")

    except json.JSONDecodeError:
        logger.error(f"Falha ao decodificar JSON da mensagem do RabbitMQ: {message_body}")
    except Exception as e:
        logger.error(f"Erro inesperado ao processar detecção: {e}", exc_info=True)
        # Em caso de erro de banco (ex: DB offline), a task pode ser re-tentada
        # raise self.retry(exc=e, countdown=60) # Descomente para retentativas