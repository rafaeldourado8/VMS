"""
TESTE RAPIDO - Envia 1 deteccao fake para testar o sistema
"""
import requests
from datetime import datetime

# Configuracoes
BACKEND_URL = "http://localhost/api/ingest/"
API_KEY = "your-ingest-api-key-here"
CAMERA_ID = 1

# Cria imagem fake (1x1 pixel vermelho)
fake_image = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00\x7f\x00\xff\xd9'

print("=" * 60)
print("TESTE RAPIDO DE DETECCAO")
print("=" * 60)

try:
    files = {'image': ('test.jpg', fake_image, 'image/jpeg')}
    
    data = {
        'camera_id': CAMERA_ID,
        'timestamp': datetime.now().isoformat(),
        'plate': 'TEST1234',
        'confidence': 0.95,
        'vehicle_type': 'car'
    }
    
    headers = {'X-API-Key': API_KEY}
    
    print(f"Enviando deteccao para: {BACKEND_URL}")
    print(f"Camera ID: {CAMERA_ID}")
    print(f"Placa: TEST1234")
    
    response = requests.post(
        BACKEND_URL,
        data=data,
        files=files,
        headers=headers,
        timeout=10
    )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 201:
        print("SUCESSO! Deteccao criada")
        print(f"Resposta: {response.json()}")
        print("\nVerifique em: http://localhost/detections")
    else:
        print(f"ERRO: {response.status_code}")
        print(f"Resposta: {response.text}")
        
except Exception as e:
    print(f"ERRO: {e}")

print("=" * 60)
