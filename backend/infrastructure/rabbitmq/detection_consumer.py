import json
import logging
import pika
import asyncio
from infrastructure.websocket.detection_manager import manager

logger = logging.getLogger(__name__)

def start_detection_consumer():
    try:
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(
            host='rabbitmq',
            port=5672,
            credentials=credentials,
            heartbeat=600
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        channel.exchange_declare(
            exchange='vms.detections',
            exchange_type='topic',
            durable=True
        )
        
        result = channel.queue_declare(queue='detections_websocket', durable=False)
        queue_name = result.method.queue
        
        channel.queue_bind(
            exchange='vms.detections',
            queue=queue_name,
            routing_key='detection.lpr.#'
        )
        
        def callback(ch, method, properties, body):
            try:
                detection = json.loads(body)
                asyncio.run(manager.broadcast(detection))
            except Exception as e:
                logger.error(f"Error processing detection: {e}")
        
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        
        logger.info("Detection consumer started")
        channel.start_consuming()
        
    except Exception as e:
        logger.error(f"Detection consumer error: {e}")
