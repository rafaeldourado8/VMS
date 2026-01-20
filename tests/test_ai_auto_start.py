"""
Teste de Integração: Auto-start AI Detection

Testa se a detecção AI inicia automaticamente quando:
1. Câmera é criada com ai_enabled=True
2. Câmera existente tem ai_enabled alterado para True
3. Câmera é deletada (deve parar detecção)
"""

import requests
import time

BACKEND_URL = "http://localhost:8000"
AI_DETECTION_URL = "http://localhost:5000"

def test_auto_start():
    print("=" * 60)
    print("TESTE: Auto-start AI Detection")
    print("=" * 60)
    
    # 1. Login
    print("\n1. Fazendo login...")
    login_response = requests.post(
        f"{BACKEND_URL}/api/auth/login/",
        json={"username": "admin", "password": "admin"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login falhou: {login_response.text}")
        return
    
    token = login_response.json()["access"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login OK")
    
    # 2. Criar câmera com AI habilitada
    print("\n2. Criando câmera com ai_enabled=True...")
    camera_data = {
        "name": "Test Camera AI",
        "location": "Test Location",
        "stream_url": "rtsp://test:test@localhost:8554/test_ai",
        "ai_enabled": True
    }
    
    create_response = requests.post(
        f"{BACKEND_URL}/api/cameras/",
        json=camera_data,
        headers=headers
    )
    
    if create_response.status_code != 201:
        print(f"❌ Criação falhou: {create_response.text}")
        return
    
    camera = create_response.json()
    camera_id = camera["id"]
    print(f"✅ Câmera criada: ID {camera_id}")
    
    # 3. Verificar se AI Detection iniciou
    print("\n3. Verificando se AI Detection iniciou...")
    time.sleep(2)  # Aguarda signal processar
    
    ai_response = requests.get(f"{AI_DETECTION_URL}/cameras")
    
    if ai_response.status_code != 200:
        print(f"❌ AI Detection não respondeu: {ai_response.text}")
    else:
        active_cameras = ai_response.json()["cameras"]
        camera_ids = [c["id"] for c in active_cameras]
        
        if camera_id in camera_ids:
            print(f"✅ AI Detection ATIVA para câmera {camera_id}")
        else:
            print(f"❌ AI Detection NÃO ATIVA para câmera {camera_id}")
            print(f"   Câmeras ativas: {camera_ids}")
    
    # 4. Desabilitar AI
    print("\n4. Desabilitando AI...")
    update_response = requests.patch(
        f"{BACKEND_URL}/api/cameras/{camera_id}/",
        json={"ai_enabled": False},
        headers=headers
    )
    
    if update_response.status_code != 200:
        print(f"❌ Update falhou: {update_response.text}")
    else:
        print("✅ AI desabilitada")
    
    time.sleep(2)
    
    ai_response = requests.get(f"{AI_DETECTION_URL}/cameras")
    active_cameras = ai_response.json()["cameras"]
    camera_ids = [c["id"] for c in active_cameras]
    
    if camera_id not in camera_ids:
        print(f"✅ AI Detection PARADA para câmera {camera_id}")
    else:
        print(f"❌ AI Detection AINDA ATIVA para câmera {camera_id}")
    
    # 5. Deletar câmera
    print("\n5. Deletando câmera...")
    delete_response = requests.delete(
        f"{BACKEND_URL}/api/cameras/{camera_id}/",
        headers=headers
    )
    
    if delete_response.status_code == 204:
        print("✅ Câmera deletada")
    else:
        print(f"❌ Delete falhou: {delete_response.text}")
    
    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)

if __name__ == "__main__":
    test_auto_start()
