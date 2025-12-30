"""
Worker FFmpeg - Extrai frames e envia para RabbitMQ
Isolado do streaming principal
"""

import asyncio
import subprocess
import json
import pika
import numpy as np
import cv2
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class FFmpegFrameExtractor:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None
        self.processes = {}
        
    def connect_rabbitmq(self):
        params = pika.URLParameters(self.rabbitmq_url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='ai_frames', durable=True)
        logger.info("✅ Conectado ao RabbitMQ")
    
    def start_extraction(self, camera_id: int, rtsp_url: str, fps: int = 1):
        """
        Inicia extração de frames (1 FPS para IA)
        Não interfere no streaming principal
        """
        cmd = [
            'ffmpeg',
            '-rtsp_transport', 'tcp',
            '-i', rtsp_url,
            '-vf', f'fps={fps}',  # 1 frame por segundo
            '-f', 'image2pipe',
            '-pix_fmt', 'bgr24',
            '-vcodec', 'rawvideo',
            '-'
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=10**8
        )
        
        self.processes[camera_id] = {
            'process': process,
            'frame_number': 0,
            'fps': fps
        }
        
        logger.info(f"🎬 Extração iniciada: Cam{camera_id} @ {fps}fps")
        
        # Inicia thread de leitura
        asyncio.create_task(self._read_frames(camera_id))
    
    async def _read_frames(self, camera_id: int):
        """Lê frames do FFmpeg e envia para RabbitMQ"""
        proc_data = self.processes[camera_id]
        process = proc_data['process']
        
        # Assume 1920x1080 (ajustar conforme necessário)
        width, height = 1920, 1080
        frame_size = width * height * 3
        
        while True:
            try:
                raw_frame = process.stdout.read(frame_size)
                
                if len(raw_frame) != frame_size:
                    logger.warning(f"Frame incompleto Cam{camera_id}")
                    break
                
                # Converte para numpy array
                frame = np.frombuffer(raw_frame, dtype=np.uint8)
                frame = frame.reshape((height, width, 3))
                
                # Codifica frame
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                frame_bytes = buffer.tobytes()
                
                # Envia para RabbitMQ
                message = {
                    'camera_id': camera_id,
                    'frame_number': proc_data['frame_number'],
                    'timestamp': datetime.now().isoformat(),
                    'frame_data': frame_bytes.hex()  # Hex para JSON
                }
                
                self.channel.basic_publish(
                    exchange='',
                    routing_key='ai_frames',
                    body=json.dumps(message),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                
                proc_data['frame_number'] += 1
                
                await asyncio.sleep(0.01)  # Pequeno delay
                
            except Exception as e:
                logger.error(f"Erro lendo frame Cam{camera_id}: {e}")
                break
        
        process.terminate()
        logger.info(f"🛑 Extração parada: Cam{camera_id}")
    
    def stop_extraction(self, camera_id: int):
        if camera_id in self.processes:
            self.processes[camera_id]['process'].terminate()
            del self.processes[camera_id]
            logger.info(f"🛑 Extração parada: Cam{camera_id}")

class AIFrameConsumer:
    """Consome frames do RabbitMQ e processa com IA"""
    
    def __init__(self, rabbitmq_url: str, detection_service):
        self.rabbitmq_url = rabbitmq_url
        self.detection_service = detection_service
        self.connection = None
        self.channel = None
        
    def connect(self):
        params = pika.URLParameters(self.rabbitmq_url)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='ai_frames', durable=True)
        self.channel.basic_qos(prefetch_count=1)
        logger.info("✅ Consumer conectado ao RabbitMQ")
    
    def start_consuming(self):
        """Inicia consumo de frames"""
        self.channel.basic_consume(
            queue='ai_frames',
            on_message_callback=self._process_message
        )
        
        logger.info("🔄 Iniciando consumo de frames...")
        self.channel.start_consuming()
    
    def _process_message(self, ch, method, properties, body):
        """Processa mensagem com frame"""
        try:
            message = json.loads(body)
            
            camera_id = message['camera_id']
            frame_number = message['frame_number']
            frame_hex = message['frame_data']
            
            # Decodifica frame
            frame_bytes = bytes.fromhex(frame_hex)
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            # Processa com serviço de detecção
            asyncio.run(
                self.detection_service.process_frame(
                    camera_id, frame, frame_number
                )
            )
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Erro processando frame: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

# Exemplo de uso
async def main():
    from detection_service import AIDetectionService, DetectionZone
    
    # Serviço de detecção
    detection_service = AIDetectionService()
    
    # Configura zona
    zone = DetectionZone(
        camera_id=1,
        p1=(100, 200),
        p2=(100, 600),
        distance_meters=20.0,
        speed_limit_kmh=60.0,
        fps=25.0
    )
    detection_service.configure_zone(zone)
    
    # Worker de processamento
    asyncio.create_task(detection_service.worker_process_queue())
    
    # Extrator FFmpeg
    extractor = FFmpegFrameExtractor('amqp://guest:guest@localhost:5672/')
    extractor.connect_rabbitmq()
    extractor.start_extraction(1, 'rtsp://camera1:554/stream', fps=1)
    
    # Consumer (rodar em processo separado)
    # consumer = AIFrameConsumer('amqp://guest:guest@localhost:5672/', detection_service)
    # consumer.connect()
    # consumer.start_consuming()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())