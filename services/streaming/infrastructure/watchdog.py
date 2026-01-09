import asyncio
import logging
import time
from typing import Dict
from prometheus_client import Counter
import pika
import json

logger = logging.getLogger(__name__)

frozen_metric = Counter(
    'vms_stream_frozen_total',
    'Total frozen stream detections',
    ['camera_id']
)


class StreamWatchdog:
    """Detects frozen streams and triggers pipeline restart"""
    
    CHECK_INTERVAL = 15
    FROZEN_THRESHOLD = 30
    
    def __init__(self, rabbitmq_url: str = "amqp://guest:guest@localhost:5672"):
        self.frame_timestamps: Dict[str, float] = {}
        self.rabbitmq_url = rabbitmq_url
        self.running = False
    
    def update_frame(self, camera_id: str):
        """Update last frame timestamp"""
        self.frame_timestamps[camera_id] = time.time()
    
    async def check_streams(self):
        """Check all streams for frozen state"""
        current_time = time.time()
        
        for camera_id, last_frame_time in list(self.frame_timestamps.items()):
            elapsed = current_time - last_frame_time
            
            if elapsed > self.FROZEN_THRESHOLD:
                logger.warning(f"🧊 Stream frozen for camera {camera_id} ({elapsed:.0f}s)")
                frozen_metric.labels(camera_id=camera_id).inc()
                await self._publish_frozen_event(camera_id)
                del self.frame_timestamps[camera_id]
    
    async def _publish_frozen_event(self, camera_id: str):
        """Publish stream.frozen event to RabbitMQ"""
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
            channel = connection.channel()
            channel.exchange_declare(exchange='vms_events', exchange_type='topic', durable=True)
            
            event = {
                'camera_id': camera_id,
                'event': 'stream.frozen',
                'timestamp': time.time()
            }
            
            channel.basic_publish(
                exchange='vms_events',
                routing_key='stream.frozen',
                body=json.dumps(event)
            )
            
            connection.close()
            logger.info(f"📤 Published stream.frozen event for camera {camera_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to publish frozen event: {e}")
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            await self.check_streams()
            await asyncio.sleep(self.CHECK_INTERVAL)
    
    async def start(self):
        """Start watchdog"""
        self.running = True
        logger.info("🐕 Stream Watchdog started")
        await self.monitor_loop()
    
    def stop(self):
        """Stop watchdog"""
        self.running = False
        logger.info("🐕 Stream Watchdog stopped")
