"""
Serviço VOD HLS - Playlist Dinâmica com Transmuxing on-the-fly
Gera playlists instantâneas e converte MP4 para TS sob demanda
"""
import os
import asyncio
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VOD HLS Dinâmico", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RECORDINGS_DIR = Path(os.getenv("RECORDINGS_DIR", "/recordings"))

@app.get("/health")
def health():
    """Health check"""
    return {"status": "ok"}

@app.get("/vod/debug")
def debug_recordings():
    """Debug: mostra estrutura do diretório de gravações"""
    info = {
        "recordings_dir": str(RECORDINGS_DIR),
        "exists": RECORDINGS_DIR.exists(),
        "is_dir": RECORDINGS_DIR.is_dir() if RECORDINGS_DIR.exists() else False,
        "contents": []
    }
    
    if RECORDINGS_DIR.exists():
        try:
            for item in RECORDINGS_DIR.iterdir():
                item_info = {
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "path": str(item)
                }
                if item.is_dir():
                    item_info["subdirs"] = []
                    for subitem in item.iterdir():
                        sub_info = {
                            "name": subitem.name,
                            "type": "dir" if subitem.is_dir() else "file"
                        }
                        if subitem.is_dir():
                            mp4_count = len(list(subitem.glob("*.mp4")))
                            sub_info["mp4_files"] = mp4_count
                        item_info["subdirs"].append(sub_info)
                info["contents"].append(item_info)
        except Exception as e:
            info["error"] = str(e)
    
    return info

@app.get("/vod/recordings")
def list_recordings():
    """Lista todas as gravações disponíveis"""
    if not RECORDINGS_DIR.exists():
        return {"error": "Diretório de gravações não existe", "path": str(RECORDINGS_DIR)}
    
    recordings = {}
    for camera_dir in RECORDINGS_DIR.iterdir():
        if not camera_dir.is_dir():
            continue
        
        camera_id = camera_dir.name.replace("camera_", "").replace("cam_", "")
        recordings[camera_id] = {}
        
        for date_dir in camera_dir.iterdir():
            if not date_dir.is_dir():
                continue
            
            mp4_files = sorted(date_dir.glob("*.mp4"))
            if mp4_files:
                recordings[camera_id][date_dir.name] = {
                    "count": len(mp4_files),
                    "first_file": mp4_files[0].stem,
                    "last_file": mp4_files[-1].stem,
                    "playlist_url": f"/vod/playlist/{camera_id}/{date_dir.name}/index.m3u8"
                }
    
    return {"recordings": recordings, "total_cameras": len(recordings)}

@app.get("/vod/playlist/{camera_id}/{date}/index.m3u8")
def get_dynamic_playlist(camera_id: int, date: str):
    """
    Gera uma playlist HLS instantânea listando todos os MP4s do dia.
    Adiciona tags de descontinuidade caso haja buracos na gravação.
    """
    camera_dir = RECORDINGS_DIR / f"camera_{camera_id}" / date
    if not camera_dir.exists():
        camera_dir = RECORDINGS_DIR / f"cam_{camera_id}" / date
        if not camera_dir.exists():
            raise HTTPException(status_code=404, detail="Gravações não encontradas")

    # Busca e ordena os arquivos MP4 (ex: 10-47-43.mp4)
    mp4_files = sorted(camera_dir.glob("*.mp4"))
    if not mp4_files:
        raise HTTPException(status_code=404, detail="Nenhum arquivo MP4 encontrado")

    m3u8_content = [
        "#EXTM3U",
        "#EXT-X-VERSION:3",
        "#EXT-X-TARGETDURATION:60",
        "#EXT-X-MEDIA-SEQUENCE:0",
        "#EXT-X-PLAYLIST-TYPE:VOD"
    ]

    last_time = None

    for mp4 in mp4_files:
        try:
            # Parse do nome do arquivo para detectar buracos (gaps) na gravação
            current_time = datetime.strptime(mp4.stem, "%H-%M-%S")
            
            if last_time:
                diff_seconds = (current_time - last_time).total_seconds()
                # Se houver um salto maior que 65 segundos, avisa o player que houve um corte
                if diff_seconds > 65:
                    m3u8_content.append("#EXT-X-DISCONTINUITY")
            
            last_time = current_time
            
            # Adiciona o segmento de 60 segundos
            m3u8_content.append("#EXTINF:60.000,")
            # Aponta para o endpoint que vai converter este MP4 sob demanda
            m3u8_content.append(f"/vod/segment/{camera_id}/{date}/{mp4.stem}.ts")
            
        except ValueError:
            continue

    m3u8_content.append("#EXT-X-ENDLIST")

    return Response(content="\n".join(m3u8_content), media_type="application/vnd.apple.mpegurl")

@app.api_route("/vod/segment/{camera_id}/{date}/{filename}.ts", methods=["GET", "HEAD"])
async def stream_ts_segment(camera_id: int, date: str, filename: str):
    """
    Converte um MP4 específico para MPEG-TS on-the-fly e faz streaming
    direto para o player, sem salvar no disco e bloqueando zero a timeline.
    """
    mp4_path = RECORDINGS_DIR / f"camera_{camera_id}" / date / f"{filename}.mp4"
    if not mp4_path.exists():
        mp4_path = RECORDINGS_DIR / f"cam_{camera_id}" / date / f"{filename}.mp4"
        
    if not mp4_path.exists():
        raise HTTPException(status_code=404, detail="Segmento MP4 não encontrado")

    cmd = [
        'ffmpeg',
        '-loglevel', 'error',
        '-i', str(mp4_path),
        '-c:v', 'copy',
        '-an',
        '-f', 'mpegts',
        '-copyts',
        '-'
    ]

    process = None
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        async def generate():
            try:
                while True:
                    chunk = await process.stdout.read(65536)
                    if not chunk:
                        break
                    yield chunk
            except Exception as e:
                print(f"[VOD] Erro no streaming de {filename}: {e}")
            finally:
                if process and process.returncode is None:
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=2)
                    except asyncio.TimeoutError:
                        process.kill()
        
        return StreamingResponse(generate(), media_type="video/MP2T")
    except Exception as e:
        if process and process.returncode is None:
            process.kill()
        print(f"[VOD] Erro ao iniciar conversão de {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
