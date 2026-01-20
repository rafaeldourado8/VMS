import pika
import json
import logging
from datetime import datetime

class RabbitMQProducer:
    def __init__(self, host='rabbitmq', port=5672, user='guest', password='guest'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
        self.channel = None
        self.logger = logging.getLogger(__name__)
        self._connect()
    
    def _connect(self):
        try:
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declara exchange
            self.channel.exchange_declare(
                exchange='vms.detections',
                exchange_type='topic',
                durable=True
            )
            
            self.logger.info("Connected to RabbitMQ")
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {e}")
            self.connection = None
            self.channel = None
    
    def send_detection(self, camera_id: int, plate: str, confidence: float, 
                      method: str, metadata: dict = None):
        if not self.channel:
            self._connect()
        
        if not self.channel:
            self.logger.error("Cannot send detection: no RabbitMQ connection")
            return False
        
        try:
            message = {
                'camera_id': camera_id,
                'plate': plate,
                'confidence': confidence,
                'method': method,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
            routing_key = f'detection.lpr.{camera_id}'
            
            self.channel.basic_publish(
                exchange='vms.detections',
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent
                    content_type='application/json'
                )
            )
            
            self.logger.info(f"Sent detection: {plate} (camera {camera_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send detection: {e}")
            self.connection = None
            self.channel = None
            return False
    
    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            self.logger.info("RabbitMQ connection closed")
