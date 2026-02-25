"""
Serviço VOD HLS - Playlist Dinâmica otimizada
"""
import os
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VOD HLS", version="2.1.0")

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
    return {"status": "ok"}

@app.get("/vod/debug")
def debug_recordings():
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
    camera_dir = RECORDINGS_DIR / f"camera_{camera_id}" / date
    if not camera_dir.exists():
        camera_dir = RECORDINGS_DIR / f"cam_{camera_id}" / date
        if not camera_dir.exists():
            raise HTTPException(404, "Gravações não encontradas")

    mp4_files = sorted(camera_dir.glob("*.mp4"))
    if not mp4_files:
        raise HTTPException(404, "Nenhum MP4")

    # Segmentos de 30s (ao invés de 10s) = menos requests
    m3u8 = ["#EXTM3U", "#EXT-X-VERSION:3", "#EXT-X-TARGETDURATION:30", "#EXT-X-PLAYLIST-TYPE:VOD"]
    
    for mp4 in mp4_files:
        # 1 minuto = 2 segmentos de 30s
        for i in range(0, 60, 30):
            m3u8.append("#EXTINF:30.0,")
            m3u8.append(f"/vod/segment/{camera_id}/{date}/{mp4.stem}_{i}.ts")

    m3u8.append("#EXT-X-ENDLIST")
    return Response("\n".join(m3u8), media_type="application/vnd.apple.mpegurl")

@app.get("/vod/segment/{camera_id}/{date}/{filename}.ts")
async def stream_ts_segment(camera_id: int, date: str, filename: str):
    base_name, chunk_str = filename.rsplit("_", 1)
    chunk_idx = int(chunk_str)
    
    mp4_path = RECORDINGS_DIR / f"camera_{camera_id}" / date / f"{base_name}.mp4"
    if not mp4_path.exists():
        mp4_path = RECORDINGS_DIR / f"cam_{camera_id}" / date / f"{base_name}.mp4"
        
    if not mp4_path.exists():
        raise HTTPException(404)

    cmd = [
        'ffmpeg', '-ss', str(chunk_idx), '-i', str(mp4_path),
        '-t', '30', '-c', 'copy', '-f', 'mpegts', '-'
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    
    async def generate():
        try:
            while True:
                chunk = await process.stdout.read(65536)
                if not chunk:
                    break
                yield chunk
        finally:
            if process.returncode is None:
                process.terminate()
    
    return StreamingResponse(generate(), media_type="video/MP2T")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
