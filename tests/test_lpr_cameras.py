import redis
import json
import time

# Conectar ao Redis
r = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

# Testar conexão
try:
    r.ping()
    print("✓ Conectado ao Redis")
except Exception as e:
    print(f"✗ Erro ao conectar ao Redis: {e}")
    exit(1)

# Publicar câmera 999 (RTSP do MediaMTX)
camera_999 = {
    "camera_id": 999,
    "rtsp_url": "rtsp://mediamtx:8554/test_video"
}

# Publicar câmera 555 (arquivo local)
camera_555 = {
    "camera_id": 555,
    "rtsp_url": "/app/test_video.mp4"
}

print("\n=== Publicando câmeras ===")
print(f"Câmera 999: {camera_999}")
r.publish("camera:provisioned", json.dumps(camera_999))
print("✓ Câmera 999 publicada")

time.sleep(2)

print(f"\nCâmera 555: {camera_555}")
r.publish("camera:provisioned", json.dumps(camera_555))
print("✓ Câmera 555 publicada")

print("\n=== Câmeras publicadas com sucesso ===")
