import redis
import json
import time

r = redis.Redis(host='redis_cache', port=6379, db=2, decode_responses=True)

try:
    r.ping()
    print("✓ Redis conectado")
except Exception as e:
    print(f"✗ Erro: {e}")
    exit(1)

cameras = [
    {"camera_id": 999, "rtsp_url": "rtsp://mediamtx:8554/test_video"},
    {"camera_id": 555, "rtsp_url": "/app/test_video.mp4"}
]

for cam in cameras:
    print(f"Publicando câmera {cam['camera_id']}: {cam['rtsp_url']}")
    r.publish("camera:provisioned", json.dumps(cam))
    time.sleep(2)

print("✓ Câmeras publicadas")
