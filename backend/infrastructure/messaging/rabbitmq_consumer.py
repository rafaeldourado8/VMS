import pika
import logging
from config.celery import app as celery_app

logger = logging.getLogger(__name__)

def start_rabbitmq_consumer():
    """Consome mensagens do RabbitMQ e envia para Celery"""
    try:
        import os
        credentials = pika.PlainCredentials(
            os.getenv('RABBITMQ_USER', 'guest'),
            os.getenv('RABBITMQ_PASS', 'guest')
        )
        parameters = pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST', 'rabbitmq'),
            port=int(os.getenv('RABBITMQ_PORT', 5672)),
            credentials=credentials,
            heartbeat=600
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Declara exchange e queue
        channel.exchange_declare(exchange='vms.detections', exchange_type='topic', durable=True)
        channel.queue_declare(queue='detections', durable=True)
        channel.queue_bind(exchange='vms.detections', queue='detections', routing_key='detection.lpr.#')
        
        def callback(ch, method, properties, body):
            try:
                celery_app.send_task('process_detection_message', args=[body.decode()])
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Detection sent to Celery")
            except Exception as e:
                logger.error(f"Error processing detection: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='detections', on_message_callback=callback)
        
        logger.info("RabbitMQ consumer started")
        channel.start_consuming()
        
    except Exception as e:
        logger.error(f"RabbitMQ consumer error: {e}")
