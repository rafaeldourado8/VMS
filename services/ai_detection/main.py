import os
import sys
import logging
import uvicorn
import threading
from ultralytics import YOLO

sys.path.append(os.path.join(os.getcwd(), 'fast-plate-ocr-master'))
from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer

from agent_manager import AgentManager
from api_server import app, set_agent_manager
from integration.rabbitmq_producer import RabbitMQProducer
from config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("AI_Main")

def main():
    logger.info(">>> INICIANDO SISTEMA TRIPLE-CORE + MOTION <<<")
    
    try:
        # ``
        logger.info("1. Carregando Vehicle Model...")
        vehicle_model = YOLO("models/vehicle_yolov8n.pt")
        
        # 2. Carrega Custom Model (Seu)
        logger.info("2. Carregando Custom Model...")
        custom_model = YOLO("models/yolov8n.pt") 
        
        # 3. Carrega Plate Model (Especialista)
        logger.info("3. Carregando Plate Model...")
        plate_model = YOLO("models/plate_yolov8n.pt")

        # 4. Carrega OCR
        logger.info("4. Carregando OCR...")
        ocr_model = LicensePlateRecognizer(hub_ocr_model="cct-xs-v1-global-model")
        
        logger.info(" Todos os modelos carregados!")
    except Exception as e:
        logger.error(f"Erro fatal ao carregar modelos: {e}")
        sys.exit(1)

    # RabbitMQ
    rabbitmq_producer = None
    try:
        rabbitmq_producer = RabbitMQProducer(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            user=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASS
        )
    except Exception as e:
        logger.error(f" Falha RabbitMQ: {e}")

    # Inicializa Manager
    agent_manager = AgentManager(
        vehicle_model=vehicle_model,
        custom_model=custom_model,
        plate_model=plate_model,
        ocr_model=ocr_model,
        backend_url=settings.BACKEND_URL,
        mediamtx_host=settings.MEDIAMTX_URL.split("://")[-1].split(":")[0],
        rabbitmq_producer=rabbitmq_producer
    )
    
    set_agent_manager(agent_manager)
    agent_manager.load_cameras_from_backend()
    
    # API Server
    api_thread = threading.Thread(
        target=uvicorn.run,
        kwargs={"app": app, "host": "0.0.0.0", "port": settings.API_PORT, "log_level": "error"},
        daemon=True
    )
    api_thread.start()
    
    try:
        api_thread.join()
    except KeyboardInterrupt:
        agent_manager.stop_all()
        if rabbitmq_producer: rabbitmq_producer.close()

if __name__ == "__main__":
    main()