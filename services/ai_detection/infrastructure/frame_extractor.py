import asyncio
import subprocess
import logging
from typing import Optional
import aio_pika
import os

logger = logging.getLogger(__name__)


class FrameExtractor:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.queue_name = "frames"

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
        self.channel = await self.connection.channel()
        await self.channel.declare_queue(self.queue_name, durable=True)
        logger.info("Connected to RabbitMQ")

    async def extract_and_publish(self, camera_id: str, rtsp_url: str):
        cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-vf", "fps=1",
            "-f", "image2pipe",
            "-vcodec", "mjpeg",
            "-q:v", "5",
            "-"
        ]

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        try:
            while True:
                frame_data = process.stdout.read(100000)
                if not frame_data:
                    break

                # Find JPEG boundaries
                start = frame_data.find(b'\xff\xd8')
                end = frame_data.find(b'\xff\xd9')
                
                if start != -1 and end != -1:
                    jpeg_frame = frame_data[start:end+2]
                    
                    message = aio_pika.Message(
                        body=jpeg_frame,
                        headers={"camera_id": camera_id},
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    )
                    
                    await self.channel.default_exchange.publish(
                        message,
                        routing_key=self.queue_name
                    )
                    logger.debug(f"Published frame for camera {camera_id}")

                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error extracting frames: {e}")
        finally:
            process.terminate()

    async def close(self):
        if self.connection:
            await self.connection.close()
