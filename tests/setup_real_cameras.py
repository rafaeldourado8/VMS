"""
Setup de Cameras Reais com Deteccao Automatica
Adiciona cameras, configura ROI e ativa IA
"""
import requests
import time

BASE_URL = "http://backend:8000"
USERNAME = "admin"
PASSWORD = "admin"

# Cameras reais
CAMERAS = [
    {"name": "Camera 01", "url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0", "location": "Ponto 1"},
    {"name": "Camera 02", "url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0", "location": "Ponto 2"},
    {"name": "Camera 03", "url": "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0", "location": "Ponto 3"},
    {"name": "Camera 04", "url": "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0", "location": "Ponto 4"},
    {"name": "Camera 05", "url": "rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0", "location": "Ponto 5"},
]

def login():
    """Faz login e retorna token"""
    print("Fazendo login...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login/",
        json={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        token = response.json()["access"]
        print(f"Login OK - Token: {token[:20]}...")
        return token
    else:
        print(f"Erro no login: {response.status_code}")
        return None

def create_camera(token, name, stream_url, location):
    """Cria camera"""
    print(f"\nCriando camera: {name}")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": name,
        "stream_url": stream_url,
        "location": location
    }
    
    response = requests.post(
        f"{BASE_URL}/api/cameras/",
        json=data,
        headers=headers
    )
    
    if response.status_code == 201:
        camera = response.json()
        print(f"  OK - ID: {camera['id']}")
        return camera
    else:
        print(f"  ERRO: {response.status_code} - {response.text[:200]}")
        return None

def configure_detection(token, camera_id):
    """Configura ROI e linhas virtuais"""
    print(f"\nConfigurando deteccao para camera {camera_id}")
    headers = {"Authorization": f"Bearer {token}"}
    
    # ROI cobrindo area central
    config = {
        "roi_areas": [
            {
                "id": "roi1",
                "name": "Area Principal",
                "points": [
                    {"x": 0.1, "y": 0.1},
                    {"x": 0.9, "y": 0.1},
                    {"x": 0.9, "y": 0.9},
                    {"x": 0.1, "y": 0.9}
                ],
                "enabled": True
            }
        ],
        "virtual_lines": [
            {
                "id": "line1",
                "name": "Linha de Contagem",
                "start": {"x": 0.2, "y": 0.5},
                "end": {"x": 0.8, "y": 0.5},
                "direction": "both",
                "enabled": True
            }
        ],
        "tripwires": [],
        "zone_triggers": [],
        "recording_retention_days": 30,
        "ai_enabled": False
    }
    
    response = requests.post(
        f"{BASE_URL}/api/cameras/{camera_id}/update_detection_config/",
        json=config,
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"  Configuracao OK")
        return True
    else:
        print(f"  ERRO: {response.status_code}")
        return False

def activate_ai(token, camera_id):
    """Ativa IA para camera"""
    print(f"\nAtivando IA para camera {camera_id}")
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/cameras/{camera_id}/toggle_ai/",
        headers=headers
    )
    
    if response.status_code == 200:
        print(f"  IA ativada")
        return True
    else:
        print(f"  ERRO: {response.status_code}")
        return False

def check_detections():
    """Verifica se ha deteccoes"""
    print("\nVerificando deteccoes...")
    response = requests.get(f"{BASE_URL}/api/detections/?page=1")
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        print(f"  Total de deteccoes: {count}")
        if count > 0:
            print(f"  Ultimas deteccoes:")
            for det in data.get('results', [])[:5]:
                print(f"    - {det.get('plate')} | {det.get('vehicle_type')} | {det.get('timestamp')}")
        return count
    return 0

def main():
    print("=" * 60)
    print("SETUP DE CAMERAS REAIS COM DETECCAO")
    print("=" * 60)
    
    # Login
    token = login()
    if not token:
        print("\nERRO: Nao foi possivel fazer login")
        return
    
    # Criar cameras
    camera_ids = []
    for cam_data in CAMERAS:
        camera = create_camera(token, cam_data["name"], cam_data["url"], cam_data["location"])
        if camera:
            camera_ids.append(camera["id"])
            time.sleep(1)
    
    print(f"\n{len(camera_ids)} cameras criadas")
    
    # Configurar deteccao
    for cam_id in camera_ids:
        configure_detection(token, cam_id)
        time.sleep(0.5)
    
    # Ativar IA
    for cam_id in camera_ids:
        activate_ai(token, cam_id)
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("SETUP CONCLUIDO!")
    print("=" * 60)
    print(f"\nCameras configuradas: {camera_ids}")
    print("\nAguardando deteccoes...")
    print("Verificando a cada 30 segundos...")
    print("Pressione Ctrl+C para parar\n")
    
    # Monitorar deteccoes
    try:
        last_count = 0
        while True:
            time.sleep(30)
            count = check_detections()
            if count > last_count:
                print(f"\n  NOVA DETECCAO! Total: {count}")
                print(f"  Verifique: {BASE_URL}/detections")
                print(f"  Imagens em: backend/media/detections/")
            last_count = count
    except KeyboardInterrupt:
        print("\n\nMonitoramento interrompido")

if __name__ == "__main__":
    main()
