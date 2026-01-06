"""
Teste Simples de Detecção - Roda no Host (Windows)
Processa vídeo local e envia detecções para o backend
"""
import cv2
import numpy as np
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações
import os
VIDEO_PATH = os.path.join(os.path.dirname(__file__), "testeplacas.mp4")
CAMERA_ID = 1
BACKEND_URL = "http://localhost/api/ingest/"  # Via HAProxy porta 80
API_KEY = "your-ingest-api-key-here"

def test_video_detection():
    """Testa detecção sem YOLO - apenas envia frames como detecções"""
    logger.info(f"🚀 Iniciando teste com vídeo: {VIDEO_PATH}")
    
    cap = cv2.VideoCapture(VIDEO_PATH)
    
    if not cap.isOpened():
        logger.error(f"❌ Não foi possível abrir vídeo: {VIDEO_PATH}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    logger.info(f"📹 Vídeo: {total_frames} frames @ {fps:.2f} FPS")
    
    frame_count = 0
    detections_sent = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Processa a cada 60 frames (aproximadamente 2 por segundo)
        if frame_count % 60 != 0:
            continue
        
        logger.info(f"🔍 Frame {frame_count}/{total_frames}")
        
        # Simula detecção - pega região central do frame
        h, w = frame.shape[:2]
        x1, y1 = w // 4, h // 4
        x2, y2 = 3 * w // 4, 3 * h // 4
        vehicle_crop = frame[y1:y2, x1:x2]
        
        # Envia como detecção
        success = send_detection(vehicle_crop, frame_count)
        if success:
            detections_sent += 1
            logger.info(f"✅ Detecção {detections_sent} enviada")
        
        # Limita a 5 detecções para teste
        if detections_sent >= 5:
            logger.info("🎯 Limite de teste atingido (5 detecções)")
            break
    
    cap.release()
    logger.info(f"🏁 Teste concluído: {detections_sent} detecções enviadas")

def send_detection(vehicle_crop, frame_num):
    """Envia detecção para o backend"""
    try:
        # Comprime imagem
        _, buffer = cv2.imencode('.jpg', vehicle_crop, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        files = {
            'image': ('detection.jpg', buffer.tobytes(), 'image/jpeg')
        }
        
        data = {
            'camera_id': CAMERA_ID,
            'timestamp': datetime.now().isoformat(),
            'plate': f"TEST{frame_num:04d}",
            'confidence': 0.85,
            'vehicle_type': 'car'
        }
        
        headers = {'X-API-Key': API_KEY}
        
        response = requests.post(
            BACKEND_URL,
            data=data,
            files=files,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 201:
            return True
        else:
            logger.error(f"❌ Erro: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro enviando detecção: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE DETECÇÃO COM VÍDEO LOCAL")
    print("=" * 60)
    print(f"Vídeo: {VIDEO_PATH}")
    print(f"Backend: {BACKEND_URL}")
    print(f"Câmera ID: {CAMERA_ID}")
    print("=" * 60)
    
    test_video_detection()
