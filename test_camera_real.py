import requests
import time

BACKEND_URL = "http://localhost:8000"
AI_SERVICE_URL = "http://localhost:5000"

RTSP_URL = "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0"

def login():
    response = requests.post(f"{BACKEND_URL}/api/auth/login/", json={
        "email": "admin@vms.com",
        "password": "admin123"
    })
    data = response.json()
    if "access" in data:
        return data["access"]
    print(f"Erro login: {data}")
    exit(1)

def create_camera(token):
    response = requests.post(
        f"{BACKEND_URL}/api/cameras/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Camera Real - Teste LPR",
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
    print("Fazendo login...")
    token = login()
    print("Login OK")
    
    print("\nCriando camera...")
    camera = create_camera(token)
    camera_id = camera["id"]
    print(f"Camera criada: ID {camera_id}")
    
    print("\nAguardando 5s...")
    time.sleep(5)
    
    print("\nIniciando IA...")
    result = start_ai_processing(camera_id)
    print(f"IA iniciada: {result}")
    
    print(f"\nRecortes em: d:\\VMS\\detections\\")
    print(f"Logs: docker-compose logs -f ai_detection")
