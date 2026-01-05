#!/usr/bin/env python3
"""
Script para testar provisionamento de câmeras reais no VMS
"""
import requests
import time
import sys

# Configuração
BACKEND_URL = "http://localhost/api"
STREAMING_URL = "http://localhost:8001"

# Câmeras reais para teste
CAMERAS = [
    {"name": "Câmera Intelbras 1", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Câmera Intelbras 2", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Câmera Intelbras 3", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Câmera Intelbras 4", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Câmera Intelbras 5", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Câmera Intelbras 6", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Câmera Intelbras 7", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.71:6046/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Câmera Intelbras 8", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.70:6045/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Câmera Intelbras 9", "rtsp_url": "rtsp://admin:Camerite123@45.236.226.70:6044/cam/realmonitor?channel=1&subtype=0"},
    {"name": "Câmera RTMP 1", "rtsp_url": "rtmp://inst-iwvio-srs-rtmp-intelbras.camerite.services:1935/record/7KOM27157189T.stream"},
    {"name": "Câmera Hikvision 1", "rtsp_url": "rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream"},
    {"name": "Câmera Hikvision 2", "rtsp_url": "rtsp://admin:Camerite@186.226.193.111:601/h264/ch1/main/av_stream"},
    {"name": "Câmera Hikvision 3", "rtsp_url": "rtsp://admin:Camerite@170.84.217.84:603/h264/ch1/main/av_stream"},
    {"name": "Câmera RTMP Hik 1", "rtsp_url": "rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487833.stream"},
    {"name": "Câmera RTMP Hik 2", "rtsp_url": "rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487237.stream"},
]

def test_backend_health():
    """Testa se o backend está respondendo"""
    try:
        response = requests.get(f"{BACKEND_URL}/health/", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_streaming_health():
    """Testa se o streaming service está respondendo"""
    try:
        response = requests.get(f"{STREAMING_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_camera(name: str, rtsp_url: str):
    """Cria uma câmera no backend"""
    try:
        payload = {
            "name": name,
            "rtsp_url": rtsp_url,
            "location": "Teste",
            "is_active": True
        }
        
        response = requests.post(
            f"{BACKEND_URL}/cameras/",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 201:
            data = response.json()
            camera_id = data.get("id")
            print(f"  ✅ Câmera criada: ID {camera_id} - {name}")
            return camera_id
        else:
            print(f"  ❌ Erro ao criar: {response.status_code} - {response.text[:100]}")
            return None
            
    except Exception as e:
        print(f"  ❌ Exceção: {e}")
        return None

def get_camera_status(camera_id: int):
    """Obtém status da câmera"""
    try:
        response = requests.get(
            f"{STREAMING_URL}/cameras/{camera_id}/status",
            timeout=5
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def delete_camera(camera_id: int):
    """Remove uma câmera"""
    try:
        response = requests.delete(
            f"{BACKEND_URL}/cameras/{camera_id}/",
            timeout=5
        )
        return response.status_code in [200, 204]
    except:
        return False

def main():
    print("=" * 70)
    print("🎥 TESTE DE PROVISIONAMENTO DE CÂMERAS REAIS")
    print("=" * 70)
    print()
    
    # Verifica serviços
    print("1️⃣ Verificando serviços...")
    if not test_backend_health():
        print("  ❌ Backend não está respondendo em", BACKEND_URL)
        return 1
    print("  ✅ Backend OK")
    
    if not test_streaming_health():
        print("  ❌ Streaming service não está respondendo em", STREAMING_URL)
        return 1
    print("  ✅ Streaming service OK")
    print()
    
    # Cria câmeras
    print(f"2️⃣ Criando {len(CAMERAS)} câmeras...")
    created_cameras = []
    
    for i, camera in enumerate(CAMERAS, 1):
        print(f"\n[{i}/{len(CAMERAS)}] {camera['name']}")
        camera_id = create_camera(camera['name'], camera['rtsp_url'])
        
        if camera_id:
            created_cameras.append(camera_id)
            time.sleep(0.5)  # Pequeno delay entre criações
    
    print()
    print(f"✅ {len(created_cameras)} câmeras criadas com sucesso!")
    print()
    
    # Verifica status
    if created_cameras:
        print("3️⃣ Verificando status das câmeras...")
        for camera_id in created_cameras[:3]:  # Verifica apenas as 3 primeiras
            status = get_camera_status(camera_id)
            if status:
                print(f"  📹 Câmera {camera_id}: {status.get('status', 'N/A')}")
        print()
    
    # Pergunta se deve limpar
    print("=" * 70)
    print(f"✅ TESTE CONCLUÍDO - {len(created_cameras)} câmeras provisionadas")
    print("=" * 70)
    print()
    print("IDs criados:", created_cameras)
    print()
    
    cleanup = input("Deseja remover as câmeras de teste? (s/N): ").strip().lower()
    
    if cleanup == 's':
        print("\n4️⃣ Removendo câmeras de teste...")
        for camera_id in created_cameras:
            if delete_camera(camera_id):
                print(f"  ✅ Câmera {camera_id} removida")
            else:
                print(f"  ⚠️ Falha ao remover câmera {camera_id}")
        print("\n✅ Limpeza concluída!")
    else:
        print("\n⚠️ Câmeras mantidas no sistema")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Teste interrompido pelo usuário")
        sys.exit(1)
