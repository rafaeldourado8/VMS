#!/usr/bin/env python3
"""
Teste de detecção LPR em tempo real
Exibe apenas a placa com maior confiança
"""
import cv2
import os
import time
from ultralytics import YOLO
from fast_plate_ocr.inference.plate_recognizer import LicensePlateRecognizer

# Configuração
RTSP_URL = os.getenv("TEST_RTSP_URL", "rtsp://mediamtx:8554/camera1")
CONFIDENCE_THRESHOLD = float(os.getenv("DETECTION_CONFIDENCE_THRESHOLD", "0.5"))

def main():
    print("🚀 Iniciando teste de detecção LPR...")
    print(f"📹 RTSP: {RTSP_URL}")
    print(f"🎯 Confiança mínima: {CONFIDENCE_THRESHOLD}")
    
    # Inicializa modelos
    print("\n⏳ Carregando modelos de IA...")
    yolo = YOLO("yolov8n.pt")
    ocr = LicensePlateRecognizer(hub_ocr_model="cct-xs-v1-global-model")
    print("✅ Modelos carregados\n")
    
    # Conecta ao stream
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print(f"❌ Erro: Não foi possível conectar ao stream {RTSP_URL}")
        return
    
    print("✅ Conectado ao stream")
    print("=" * 60)
    
    frame_count = 0
    last_detection_time = 0
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️  Stream perdido, tentando reconectar...")
                time.sleep(2)
                cap = cv2.VideoCapture(RTSP_URL)
                continue
            
            frame_count += 1
            
            # Processa a cada 3 frames (otimização)
            if frame_count % 3 != 0:
                continue
            
            # Detecta placas com YOLO
            results = yolo(frame, classes=[2, 7], conf=CONFIDENCE_THRESHOLD, verbose=False)
            
            best_detection = None
            best_confidence = 0.0
            
            for result in results:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    
                    if conf > best_confidence:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        crop = frame[y1:y2, x1:x2]
                        
                        # OCR na placa
                        try:
                            plates = ocr.run([crop])
                            if plates and plates[0]:
                                best_detection = {
                                    'plate': plates[0],
                                    'confidence': conf,
                                    'bbox': (x1, y1, x2, y2)
                                }
                                best_confidence = conf
                        except Exception as e:
                            print(f"⚠️  Erro no OCR: {e}")
            
            # Exibe apenas a melhor detecção
            if best_detection:
                current_time = time.time()
                # Evita spam (1 detecção por segundo)
                if current_time - last_detection_time >= 1.0:
                    print("\n" + "=" * 60)
                    print(f"🚗 DETECÇÃO")
                    print(f"📋 Placa: {best_detection['plate']}")
                    print(f"🎯 Confiança: {best_detection['confidence']:.2%}")
                    print(f"📍 BBox: {best_detection['bbox']}")
                    print(f"⏰ Timestamp: {time.strftime('%H:%M:%S')}")
                    print("=" * 60)
                    last_detection_time = current_time
            
            # Pequeno delay
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Teste interrompido pelo usuário")
    finally:
        cap.release()
        print("✅ Stream fechado")

if __name__ == "__main__":
    main()
