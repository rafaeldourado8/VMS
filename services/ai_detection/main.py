"""
Main - Serviço de IA com Trigger P1-P2
"""

import asyncio
import logging
import os
from detection_service import AIDetectionService, DetectionZone
from ffmpeg_worker import AIFrameConsumer
from database import DetectionDatabase

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    worker_id = os.getenv('WORKER_ID', '1')
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://ai_user:ai_pass@rabbitmq_ai:5672/')
    redis_url = os.getenv('REDIS_URL', 'redis://redis_ai:6379/3')
    db_url = os.getenv('DB_URL', 'postgresql://ai_user:ai_pass@postgres_ai/ai_detections')
    
    logger.info(f"🚀 Iniciando AI Worker {worker_id}")
    
    # Inicializa banco de dados
    db = DetectionDatabase(db_url)
    logger.info("✅ Banco de dados inicializado")
    
    # Carrega configurações de zonas
    # TODO: Carregar do banco
    
    # Serviço de detecção
    detection_service = AIDetectionService()
    
    # Exemplo: Configura zona para câmera 1
    zone = DetectionZone(
        camera_id=1,
        p1=(100, 200),
        p2=(100, 600),
        distance_meters=20.0,
        speed_limit_kmh=60.0,
        fps=25.0
    )
    detection_service.configure_zone(zone)
    
    # Inicia worker de processamento
    asyncio.create_task(detection_service.worker_process_queue())
    logger.info("✅ Worker de processamento iniciado")
    
    # Consumer de frames
    consumer = AIFrameConsumer(rabbitmq_url, detection_service)
    consumer.connect()
    logger.info("✅ Consumer conectado ao RabbitMQ")
    
    # Inicia consumo (blocking)
    logger.info(f"🔄 Worker {worker_id} pronto para processar frames")
    consumer.start_consuming()

if __name__ == "__main__":
    asyncio.run(main())