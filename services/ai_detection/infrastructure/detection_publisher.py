import aio_pika
import json
from typing import Optional
from domain.detection_result import DetectionResult
import logging

logger = logging.getLogger(__name__)


class DetectionPublisher:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
    
    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            'detections',
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )
        logger.info("DetectionPublisher connected")
    
    async def publish(self, result: DetectionResult):
        message = aio_pika.Message(
            body=result.model_dump_json().encode(),
            content_type='application/json',
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        
        routing_key = f"detection.{result.provider}.{result.camera_id}"
        await self.exchange.publish(message, routing_key=routing_key)
        logger.debug(f"Published detection: {routing_key}")
    
    async def close(self):
        if self.connection:
            await self.connection.close()
