"""
Main - Serviço de IA com Trigger P1-P2 e Gerenciamento Automático de Câmeras
"""

import asyncio
import logging
import os
from detection_service import AIDetectionService, DetectionZone
from ffmpeg_worker import AIFrameConsumer
from database import DetectionDatabase
from camera_manager import CameraManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    worker_id = os.getenv('WORKER_ID', '1')
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://gtvision_user:your-rabbitmq-password-here@rabbitmq:5672/')
    redis_url = os.getenv('REDIS_URL', 'redis://redis_cache:6379/3')
    db_url = os.getenv('DB_URL', 'postgresql://gtvision_user:your-strong-password-here@postgres_db/gtvision_db')
    backend_url = os.getenv('BACKEND_URL', 'http://backend:8000')
    
    logger.info(f"🚀 Iniciando AI Worker {worker_id}")
    
    # Inicializa banco de dados
    db = DetectionDatabase(db_url)
    logger.info("✅ Banco de dados inicializado")
    
    # Serviço de detecção
    detection_service = AIDetectionService()
    
    # Carrega configurações de zonas do banco
    # TODO: Implementar carregamento dinâmico
    
    # Inicia worker de processamento
    asyncio.create_task(detection_service.worker_process_queue())
    logger.info("✅ Worker de processamento iniciado")
    
    # Se for o worker 1, inicia o gerenciador de câmeras
    if worker_id == '1':
        camera_manager = CameraManager(rabbitmq_url, backend_url)
        asyncio.create_task(camera_manager.start())
        logger.info("✅ Gerenciador de câmeras iniciado")
    
    # Consumer de frames
    consumer = AIFrameConsumer(rabbitmq_url, detection_service)
    consumer.connect()
    logger.info("✅ Consumer conectado ao RabbitMQ")
    
    # Inicia consumo (blocking)
    logger.info(f"🔄 Worker {worker_id} pronto para processar frames")
    consumer.start_consuming()

if __name__ == "__main__":
    asyncio.run(main())