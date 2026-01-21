import os
import sys
import logging
import uvicorn
import threading
from ultralytics import YOLO

# Ajuste de path para encontrar a lib de OCR local
sys.path.append(os.path.join(os.getcwd(), 'fast-plate-ocr-master'))
from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer

from agent_manager import AgentManager
from api_server import app, set_agent_manager

# Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("AI_Manager")

# Variáveis de Ambiente
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
MEDIAMTX_HOST = os.getenv("MEDIAMTX_HOST", "mediamtx")
API_PORT = int(os.getenv("API_PORT", "5000"))

def main():
    logger.info(">>> INICIANDO SERVIÇO DE IA (MULTI-THREAD) <<<")
    
    # 1. Carregar Modelos
    logger.info("1. Carregando Modelos YOLO e OCR...")
    try:
        yolo_model = YOLO("models/plate_yolov8n.pt")
        ocr_model = LicensePlateRecognizer(hub_ocr_model="cct-xs-v1-global-model")
        logger.info(" Modelos carregados com sucesso!")
    except Exception as e:
        logger.error(f"Erro fatal ao carregar modelos: {e}")
        sys.exit(1)

    # 2. Inicializar Agent Manager
    agent_manager = AgentManager(
        yolo_model=yolo_model,
        ocr_model=ocr_model,
        backend_url=BACKEND_URL,
        mediamtx_host=MEDIAMTX_HOST
    )
    
    # Injetar no módulo API
    set_agent_manager(agent_manager)
    
    # 3. Carregar câmeras iniciais do backend
    logger.info("2. Carregando câmeras do backend...")
    agent_manager.load_cameras_from_backend()
    
    # 4. Iniciar API em thread separada
    logger.info(f"3. Iniciando API na porta {API_PORT}...")
    api_thread = threading.Thread(
        target=uvicorn.run,
        kwargs={
            "app": app,
            "host": "0.0.0.0",
            "port": API_PORT,
            "log_level": "info"
        },
        daemon=True
    )
    api_thread.start()
    
    # 5. Manter serviço rodando
    logger.info("✅ Serviço iniciado com sucesso!")
    try:
        api_thread.join()
    except KeyboardInterrupt:
        logger.info("Parando serviços...")
        agent_manager.stop_all()

if __name__ == "__main__":
    main()