import sys
import os
import cv2
import json
import time
import uuid
from datetime import datetime

# --- TRUQUE PARA USAR O OCR LOCAL (DO ANTIGO) ---
# Adiciona a pasta copiada ao path do Python
sys.path.append(os.path.join(os.getcwd(), 'fast-plate-ocr-master'))

from ultralytics import YOLO
# Importa direto da pasta local que você copiou
from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer

# --- CONFIGURAÇÕES ---
RTSP_URL = "rtsp://mediamtx:8554/cam"
OUTPUT_DIR = "/app/detections_sandbox"
# Caminho do modelo que você copiou
MODEL_PATH = "models/plate_yolov8n.pt" 

os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print(">>> Iniciando Sandbox Híbrido (Core Antigo no Ambiente Novo)...")

    # 1. Carregar YOLO
    try:
        print(f"Carregando YOLO de {MODEL_PATH}...")
        yolo_model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f" Erro ao carregar YOLO. Você copiou o modelo para {MODEL_PATH}? Erro: {e}")
        return

    # 2. Carregar OCR (Da pasta local)
    print("Carregando OCR Local...")
    try:
        ocr = LicensePlateRecognizer(hub_ocr_model="cct-xs-v1-global-model")
    except Exception as e:
        print(f" Erro ao carregar OCR. Verifique a pasta fast-plate-ocr-master. Erro: {e}")
        return

    # 3. Conectar ao Stream
    print(f"Conectando ao RTSP: {RTSP_URL}")
    cap = cv2.VideoCapture(RTSP_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("! Falha ao ler frame. Reconectando...")
            time.sleep(2)
            cap.open(RTSP_URL)
            continue

        # Detecção YOLO
        results = yolo_model(frame, verbose=False, conf=0.5)
        
        for result in results:
            for box in result.boxes:
                # Recorte da placa
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                plate_crop = frame[y1:y2, x1:x2]
                
                # OCR na placa
                try:
                    # O OCR espera uma lista de imagens
                    texts = ocr.run([plate_crop])
                    plate_text = texts[0]
                    
                    if plate_text and len(plate_text) > 3: # Filtro básico
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename_base = f"{OUTPUT_DIR}/{plate_text}_{timestamp}"
                        
                        # Salvar
                        cv2.imwrite(f"{filename_base}.jpg", plate_crop)
                        
                        json_data = {
                            "plate": plate_text,
                            "timestamp": timestamp,
                            "confidence_yolo": float(box.conf[0])
                        }
                        with open(f"{filename_base}.json", "w") as f:
                            json.dump(json_data, f, indent=4)
                            
                        print(f" PLACA: {plate_text} -> Salvo.")
                        
                except Exception as e:
                    print(f"Erro no OCR: {e}")

if __name__ == "__main__":
    main()