"""
Serviço VOD HLS - Converte MP4 para HLS on-demand
Serve gravações como HLS sem interferir no streaming ao vivo
"""
import os
import subprocess
import hashlib
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VOD HLS Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretórios
RECORDINGS_DIR = Path(os.getenv("RECORDINGS_DIR", "/recordings"))
HLS_CACHE_DIR = Path(os.getenv("HLS_CACHE_DIR", "/hls_cache"))
HLS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Controle de cache ativo por câmera
active_camera_cache = {}

def get_cache_path(mp4_path: str) -> Path:
    """Gera path do cache HLS baseado no hash do arquivo MP4"""
    file_hash = hashlib.md5(mp4_path.encode()).hexdigest()
    return HLS_CACHE_DIR / file_hash

def convert_to_hls(mp4_path: Path, output_dir: Path):
    """Converte MP4 para HLS usando FFmpeg"""
    output_dir.mkdir(parents=True, exist_ok=True)
    playlist_path = output_dir / "index.m3u8"
    
    if playlist_path.exists():
        return  # Já convertido
    
    cmd = [
        'ffmpeg',
        '-i', str(mp4_path),
        '-c:v', 'copy',
        '-c:a', 'copy',
        '-f', 'hls',
        '-hls_time', '2',
        '-hls_list_size', '0',
        '-hls_flags', 'independent_segments',
        '-hls_segment_filename', str(output_dir / 'segment%03d.ts'),
        str(playlist_path)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)

@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok"}

@app.post("/cache/start/{camera_id}")
def start_cache(camera_id: int, date: str = None):
    """Inicia cache para uma câmera específica"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    active_camera_cache[camera_id] = {
        "date": date,
        "started_at": datetime.now()
    }
    
    return {"status": "cache_started", "camera_id": camera_id, "date": date}

@app.post("/cache/stop/{camera_id}")
def stop_cache(camera_id: int):
    """Para cache e limpa arquivos de uma câmera"""
    if camera_id in active_camera_cache:
        del active_camera_cache[camera_id]
    
    # Limpar cache da câmera
    camera_pattern = f"camera_{camera_id}"
    cleaned = 0
    
    for cache_dir in HLS_CACHE_DIR.iterdir():
        if cache_dir.is_dir():
            # Verificar se o cache pertence a esta câmera
            for file in cache_dir.iterdir():
                if camera_pattern in str(file):
                    shutil.rmtree(cache_dir)
                    cleaned += 1
                    break
    
    return {"status": "cache_stopped", "camera_id": camera_id, "cleaned": cleaned}

@app.post("/cache/cleanup")
def cleanup_old_cache():
    """Limpa cache com mais de 24 horas"""
    cutoff = datetime.now() - timedelta(hours=24)
    cleaned = 0
    
    for cache_dir in HLS_CACHE_DIR.iterdir():
        if cache_dir.is_dir():
            # Verificar idade do cache
            mtime = datetime.fromtimestamp(cache_dir.stat().st_mtime)
            if mtime < cutoff:
                shutil.rmtree(cache_dir)
                cleaned += 1
    
    return {"status": "cleanup_complete", "cleaned": cleaned}

@app.get("/vod/{video_path:path}/index.m3u8")
def serve_playlist(video_path: str):
    """Serve playlist HLS"""
    print(f"[VOD] Requisicao: {video_path}")
    
    # Tentar com camera_{id} se vier apenas o ID
    if video_path.split('/')[0].isdigit():
        parts = video_path.split('/', 1)
        video_path = f"camera_{parts[0]}/{parts[1]}"
    
    mp4_path = RECORDINGS_DIR / video_path
    print(f"[VOD] Procurando: {mp4_path}")
    
    if not mp4_path.exists():
        # Tentar com cam_ ao invés de camera_
        alt_path = str(mp4_path).replace('camera_', 'cam_')
        mp4_path = Path(alt_path)
        print(f"[VOD] Tentando alternativo: {mp4_path}")
        
        if not mp4_path.exists():
            print(f"[VOD] Arquivo nao encontrado: {video_path}")
            raise HTTPException(status_code=404, detail=f"Video not found: {video_path}")
    
    cache_dir = get_cache_path(str(mp4_path))
    
    try:
        convert_to_hls(mp4_path, cache_dir)
        return FileResponse(
            cache_dir / "index.m3u8",
            media_type="application/vnd.apple.mpegurl"
        )
    except Exception as e:
        print(f"[VOD] Erro na conversao: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")

@app.get("/vod/{video_path:path}/{segment}")
def serve_segment(video_path: str, segment: str):
    """Serve segmento HLS"""
    # Tentar com camera_{id} se vier apenas o ID
    if video_path.split('/')[0].isdigit():
        parts = video_path.split('/', 1)
        video_path = f"camera_{parts[0]}/{parts[1]}"
    
    mp4_path = RECORDINGS_DIR / video_path
    
    # Tentar cam_ se camera_ nao existir
    if not mp4_path.exists():
        alt_path = str(mp4_path).replace('camera_', 'cam_')
        mp4_path = Path(alt_path)
    
    cache_dir = get_cache_path(str(mp4_path))
    segment_path = cache_dir / segment
    
    if not segment_path.exists():
        raise HTTPException(status_code=404, detail="Segment not found")
    
    return FileResponse(segment_path, media_type="video/MP2T")

if __name__ == "__main__":
    import uvicorn
    import asyncio
    from threading import Thread
    
    def cleanup_task():
        """Task para limpar cache antigo a cada hora"""
        import time
        while True:
            time.sleep(3600)  # 1 hora
            try:
                cutoff = datetime.now() - timedelta(hours=24)
                cleaned = 0
                for cache_dir in HLS_CACHE_DIR.iterdir():
                    if cache_dir.is_dir():
                        mtime = datetime.fromtimestamp(cache_dir.stat().st_mtime)
                        if mtime < cutoff:
                            shutil.rmtree(cache_dir)
                            cleaned += 1
                print(f"[Cache Cleanup] Removidos {cleaned} caches antigos")
            except Exception as e:
                print(f"[Cache Cleanup] Erro: {e}")
    
    # Iniciar thread de limpeza
    cleanup_thread = Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    
    uvicorn.run(app, host="0.0.0.0", port=8004)
