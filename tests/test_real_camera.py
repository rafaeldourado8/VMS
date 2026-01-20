import requests
import time

BACKEND_URL = "http://localhost:8000"
AI_SERVICE_URL = "http://localhost:5000"

# Câmera real
RTSP_URL = "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0"

def login():
    response = requests.post(f"{BACKEND_URL}/api/auth/login/", json={
        "username": "admin",
        "password": "admin"
    })
    return response.json()["access"]

def create_camera(token):
    response = requests.post(
        f"{BACKEND_URL}/api/cameras/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Câmera Real - Teste LPR",
            "stream_url": RTSP_URL,
            "location": "Teste",
            "ai_enabled": True
        }
    )
    return response.json()

def start_ai_processing(camera_id):
    response = requests.post(
        f"{AI_SERVICE_URL}/cameras/{camera_id}/start",
        headers={"Content-Type": "application/json"},
        json={}
    )
    return response.json()

if __name__ == "__main__":
    print("🔐 Fazendo login...")
    token = login()
    print("✅ Login OK")
    
    print("\n📹 Criando câmera...")
    camera = create_camera(token)
    camera_id = camera["id"]
    print(f"✅ Câmera criada: ID {camera_id}")
    
    print("\n⏳ Aguardando 5s para MediaMTX provisionar...")
    time.sleep(5)
    
    print("\n🤖 Iniciando processamento de IA...")
    result = start_ai_processing(camera_id)
    print(f"✅ IA iniciada: {result}")
    
    print(f"\n✨ Tudo pronto!")
    print(f"📂 Recortes serão salvos em: d:\\VMS\\detections\\")
    print(f"📊 Monitore: docker-compose logs -f ai_detection")
