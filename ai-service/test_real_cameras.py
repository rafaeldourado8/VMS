import cv2
import requests
import base64
import time
from datetime import datetime

API_URL = "http://localhost:8080"

CAMERAS = [
    {"id": 1, "url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0", "name": "Camera 1"},
    {"id": 2, "url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0", "name": "Camera 2"},
    {"id": 3, "url": "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0", "name": "Camera 3"},
    {"id": 4, "url": "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0", "name": "Camera 4"},
]

def capture_frame(rtsp_url, timeout=10):
    cap = cv2.VideoCapture(rtsp_url)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    start = time.time()
    while time.time() - start < timeout:
        ret, frame = cap.read()
        if ret:
            cap.release()
            return frame
    
    cap.release()
    return None

def send_detection(camera_id, frame):
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    payload = {"camera_id": camera_id, "image_base64": img_base64}
    
    start = time.time()
    response = requests.post(f"{API_URL}/detect", json=payload, timeout=30)
    elapsed = (time.time() - start) * 1000
    
    return response.json(), elapsed

def test_camera(camera):
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Testando {camera['name']}")
    print(f"URL: {camera['url']}")
    print(f"{'='*60}")
    
    print("Capturando frame...")
    frame = capture_frame(camera['url'])
    
    if frame is None:
        print("❌ ERRO: Não foi possível capturar frame")
        return
    
    h, w = frame.shape[:2]
    print(f"✅ Frame capturado: {w}x{h}")
    
    print("Enviando para detecção...")
    try:
        result, elapsed = send_detection(camera['id'], frame)
        
        print(f"⏱️  Tempo de processamento: {elapsed:.2f}ms")
        print(f"🔍 Detecções encontradas: {len(result['detections'])}")
        
        if result['detections']:
            print("\nDetalhes:")
            for i, det in enumerate(result['detections'], 1):
                print(f"\n  [{i}] {det['object_type'].upper()}")
                print(f"      Confiança: {det['confidence']:.2%}")
                print(f"      BBox: x={det['bbox']['x']}, y={det['bbox']['y']}, w={det['bbox']['w']}, h={det['bbox']['h']}")
                
                if det.get('plate_number'):
                    print(f"      🚗 Placa: {det['plate_number']} (conf: {det.get('vehicle_confidence', 0):.2%})")
                
                if det.get('vehicle_model'):
                    print(f"      🚙 Modelo: {det['vehicle_model']}")
        else:
            print("ℹ️  Nenhum veículo detectado neste frame")
            
    except Exception as e:
        print(f"❌ ERRO na detecção: {e}")

def test_all_cameras():
    print("\n" + "="*60)
    print("TESTE DE DETECÇÃO COM CÂMERAS REAIS")
    print("="*60)
    
    # Health check
    try:
        health = requests.get(f"{API_URL}/health", timeout=5).json()
        print(f"\n✅ AI Service: {health['status']}")
        print(f"   Workers processados: {health['processed_total']}")
        print(f"   Tempo médio: {health['avg_processing_time_ms']:.2f}ms")
        print(f"   GPU disponível: {'Sim' if health['gpu_available'] else 'Não'}")
    except Exception as e:
        print(f"\n❌ AI Service não está respondendo: {e}")
        return
    
    # Test each camera
    for camera in CAMERAS:
        test_camera(camera)
        time.sleep(2)
    
    print("\n" + "="*60)
    print("TESTE CONCLUÍDO")
    print("="*60)

if __name__ == "__main__":
    test_all_cameras()
