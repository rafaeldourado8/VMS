import subprocess
import redis
from fastapi import HTTPException

# Configuração do Redis (Ideal mover para .env)
r = redis.Redis(host='redis', port=6379, db=0)

def get_camera_thumbnail(rtsp_url: str, camera_id: str):
    cache_key = f"thumb:{camera_id}"
    cached_image = r.get(cache_key)
    
    if cached_image:
        return cached_image

    # Comando FFmpeg otimizado para extração rápida de 1 frame
    command = [
        'ffmpeg',
        '-rtsp_transport', 'tcp', # Força TCP para evitar perda de pacotes
        '-i', rtsp_url,
        '-f', 'image2',
        '-vframes', '1',
        '-vf', 'scale=320:-1', # Reduz tamanho para thumbnail (performance)
        '-'
    ]
    
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate(timeout=5) # Timeout para não travar
        
        if process.returncode == 0:
            # Cache por 30 segundos
            r.setex(cache_key, 30, output)
            return output
        else:
            print(f"Erro FFmpeg: {error}")
            return None
    except Exception as e:
        print(f"Erro ao gerar thumbnail: {e}")
        return None