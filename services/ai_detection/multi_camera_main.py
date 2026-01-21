import sys
import os
import time

# Hacks de path para imports funcionarem
sys.path.append(os.path.join(os.getcwd(), 'fast-plate-ocr-master'))

from ultralytics import YOLO
from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer
from camera_agent import CameraAgent

# Configurações
MODEL_YOLO = "models/plate_yolov8n.pt"
OUTPUT_DIR = "/app/detections_sandbox"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# LISTA DE CÂMERAS (Adicione quantas quiser aqui)
CAMERAS_CONFIG = [
    {
        "id": "cam_teste_1",
        "url": "rtsp://mediamtx:8554/cam" # Sua câmera proxy do mediamtx.yml
    },
    # Exemplo de como adicionar a segunda (se configurar no mediamtx.yml)
    # { "id": "portaria_2", "url": "rtsp://mediamtx:8554/outra_cam" }
]

def main():
    print(">>> INICIANDO SERVIÇO MULTI-CÂMERA <<<")
    
    # 1. Carrega Modelos (Singleton - Compartilhado entre todas as threads)
    print("1. Carregando Modelos na Memória...")
    try:
        yolo_shared = YOLO(MODEL_YOLO)
        ocr_shared = LicensePlateRecognizer(hub_ocr_model="cct-xs-v1-global-model")
        print(" Modelos Carregados!")
    except Exception as e:
        print(f" Erro fatal ao carregar modelos: {e}")
        return

    agents = []

    # 2. Inicializa Agentes
    print(f"2. Iniciando {len(CAMERAS_CONFIG)} câmeras...")
    
    for cam_conf in CAMERAS_CONFIG:
        agent = CameraAgent(
            camera_id=cam_conf["id"],
            rtsp_url=cam_conf["url"],
            yolo_model=yolo_shared,   # Passa a referência do modelo já carregado
            ocr_model=ocr_shared,     # Passa a referência do OCR
            output_dir=OUTPUT_DIR
        )
        agent.start()
        agents.append(agent)
    
    print(">>> SISTEMA OPERANDO. Pressione Ctrl+C para parar. <<<")

    # 3. Mantém o processo vivo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nParando serviços...")
        for agent in agents:
            agent.stop()

if __name__ == "__main__":
    main()