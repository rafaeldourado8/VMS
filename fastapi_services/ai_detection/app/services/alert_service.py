import pika
import logging
import json
from ..config import rabbitmq_settings, settings
from ..schemas import DetectionResult
import time

logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        self.amqp_url = rabbitmq_settings.get_amqp_url()
        self.queue_name = rabbitmq_settings.queue
        logger.info(f"AlertService configurado para fila: {self.queue_name} em {rabbitmq_settings.host}")

    def _get_channel(self):
        """
        Cria uma nova conexão e canal.
        Isto é mais seguro para ambientes com threads como FastAPI.
        """
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self.amqp_url))
            channel = connection.channel()
            
            # Garante que a fila existe e é durável (sobrevive a reinícios)
            channel.queue_declare(queue=self.queue_name, durable=True)
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"Falha ao conectar/declarar fila no RabbitMQ: {e}")
            time.sleep(5) # Espera antes de tentar de novo
            return None, None

    def send_detection_alert(self, detection_data: DetectionResult):
        """
        Publica uma mensagem de detecção no RabbitMQ.
        """
        connection, channel = None, None
        try:
            connection, channel = self._get_channel()
            
            if not channel:
                logger.error("Não foi possível obter canal do RabbitMQ. Mensagem perdida.")
                return

            message_body = detection_data.model_dump_json()

            channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Torna a mensagem persistente
                )
            )
            logger.debug(f"Mensagem de detecção para {detection_data.camera_id} publicada na fila.")
            
        except Exception as e:
            logger.error(f"Erro ao publicar mensagem no RabbitMQ: {e}")
        finally:
            if connection and connection.is_open:
                connection.close()
            
# Instancia o serviço
alert_service = AlertService()