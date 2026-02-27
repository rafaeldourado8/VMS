import asyncio
import os
import json
import hashlib
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Clips Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

CLIPS_DIR = Path("/clips")
RECORDINGS_DIR = Path("/recordings")
DB_FILE = CLIPS_DIR / "clips_db.json"
CLIPS_DIR.mkdir(exist_ok=True)

def get_video_duration(file_path):
    """Obtém duração do vídeo usando ffprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(file_path)],
            capture_output=True, text=True, timeout=5
        )
        return int(float(result.stdout.strip()))
    except:
        return 0

def load_db():
    if DB_FILE.exists():
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db():
    with open(DB_FILE, 'w') as f:
        json.dump(clips_db, f, indent=2)

def migrate_orphan_clips():
    """Migra clips órfãos (MP4s sem metadados no JSON)"""
    existing_ids = set(clips_db.keys())
    migrated = 0
    
    for mp4 in CLIPS_DIR.glob("*.mp4"):
        clip_id = mp4.stem
        if clip_id in existing_ids:
            continue
        
        stat = mp4.stat()
        duration = get_video_duration(mp4)
        
        clips_db[clip_id] = {
            "camera_id": 0,
            "start_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "end_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "status": "completed",
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "file_size": stat.st_size,
            "duration": duration,
            "file_path": str(mp4)
        }
        migrated += 1
        print(f"[MIGRATE] {clip_id} ({duration}s)")
    
    if migrated > 0:
        save_db()
        print(f"[MIGRATE] ✅ {migrated} clips migrados")

clips_db = load_db()
migrate_orphan_clips()

class ClipRequest(BaseModel):
    camera_id: int
    start_time: str
    end_time: str
    format: str = "mp4"
    quality: str = "medium"
    name: Optional[str] = None

class ClipResponse(BaseModel):
    id: str
    status: str
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None

async def create_clip_task(clip_id: str, camera_id: int, start_time: str, end_time: str, quality: str):
    try:
        clips_db[clip_id]["status"] = "processing"
        save_db()
        print(f"[CLIP] Processando: {clip_id}")
        
        # Remover timezone e usar horário local
        start_dt = datetime.fromisoformat(start_time.replace('Z', '').split('+')[0].split('-03:00')[0])
        end_dt = datetime.fromisoformat(end_time.replace('Z', '').split('+')[0].split('-03:00')[0])
        duration = int((end_dt - start_dt).total_seconds())
        
        print(f"[CLIP] Intervalo: {start_dt} a {end_dt}")
        
        if duration > 600:
            raise Exception("Máximo: 10 minutos")
        
        date_str = start_dt.strftime("%Y-%m-%d")
        recording_dir = RECORDINGS_DIR / f"camera_{camera_id}" / date_str
        
        print(f"[CLIP] Buscando em: {recording_dir}")
        
        if not recording_dir.exists():
            raise Exception(f"Sem gravações: {date_str}")
        
        recordings = sorted(recording_dir.glob("*.mp4"))
        print(f"[CLIP] Encontrados {len(recordings)} arquivos MP4")
        
        if not recordings:
            raise Exception("Nenhum MP4 encontrado")
        
        # Encontrar arquivos relevantes
        relevant = []
        for rec in recordings:
            try:
                parts = rec.stem.split('-')
                if len(parts) >= 3:
                    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
                    file_dt = start_dt.replace(hour=h, minute=m, second=s)
                    if file_dt <= end_dt and (file_dt + timedelta(seconds=60)) >= start_dt:
                        relevant.append((file_dt, rec))
                        print(f"[CLIP] Arquivo relevante: {rec.name} ({file_dt})")
            except:
                continue
        
        print(f"[CLIP] Total relevantes: {len(relevant)}")
        
        if not relevant:
            raise Exception("Nenhum segmento no intervalo")
        
        relevant.sort()
        output = CLIPS_DIR / f"{clip_id}.mp4"
        thumbnail = CLIPS_DIR / f"{clip_id}.jpg"
        
        # Criar lista de concatenação com caminhos absolutos
        concat_file = CLIPS_DIR / f"{clip_id}_concat.txt"
        with open(concat_file, 'w') as f:
            for _, rec in relevant:
                # Usar caminho absoluto e escapar aspas
                f.write(f"file '{str(rec).replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'\n")
        
        offset = int((start_dt - relevant[0][0]).total_seconds())
        
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-ss", str(max(0, offset)),
            "-t", str(duration),
            "-c", "copy",
            "-movflags", "+faststart",
            "-avoid_negative_ts", "make_zero",
            str(output)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg: {stderr.decode()[-200:]}")
        
        if output.exists() and output.stat().st_size > 0:
            # Gerar thumbnail
            thumb_cmd = [
                "ffmpeg", "-y", "-i", str(output),
                "-ss", "1", "-vframes", "1",
                "-vf", "scale=320:-1",
                str(thumbnail)
            ]
            await asyncio.create_subprocess_exec(*thumb_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            
            clips_db[clip_id].update({
                "status": "completed",
                "file_size": output.stat().st_size,
                "duration": duration,
                "file_path": str(output),
                "thumbnail": str(thumbnail) if thumbnail.exists() else None
            })
            save_db()
            concat_file.unlink()
            print(f"[CLIP] Concluído: {clip_id}")
        else:
            raise Exception("Arquivo vazio")
            
    except Exception as e:
        clips_db[clip_id]["status"] = "failed"
        clips_db[clip_id]["error"] = str(e)
        save_db()
        print(f"[CLIP ERRO] {clip_id}: {e}")

@app.post("/clips/create", response_model=ClipResponse)
async def create_clip(request: ClipRequest, background_tasks: BackgroundTasks):
    clip_id = hashlib.md5(f"{request.camera_id}{request.start_time}{request.end_time}".encode()).hexdigest()
    
    if clip_id in clips_db:
        return ClipResponse(
            id=clip_id,
            status=clips_db[clip_id]["status"],
            download_url=f"/clips/{clip_id}/download" if clips_db[clip_id]["status"] == "completed" else None
        )
    
    clips_db[clip_id] = {
        "camera_id": request.camera_id,
        "start_time": request.start_time,
        "end_time": request.end_time,
        "status": "pending",
        "name": request.name or f"Clip Camera {request.camera_id}",
        "created_at": datetime.now().isoformat()
    }
    save_db()
    
    background_tasks.add_task(create_clip_task, clip_id, request.camera_id, request.start_time, request.end_time, request.quality)
    
    return ClipResponse(id=clip_id, status="pending")

@app.get("/clips/{clip_id}", response_model=ClipResponse)
async def get_clip(clip_id: str):
    if clip_id not in clips_db:
        raise HTTPException(status_code=404, detail="Clip não encontrado")
    
    clip = clips_db[clip_id]
    return ClipResponse(
        id=clip_id,
        status=clip["status"],
        download_url=f"/clips/{clip_id}/download" if clip["status"] == "completed" else None,
        file_size=clip.get("file_size"),
        duration=clip.get("duration")
    )

@app.get("/clips/{clip_id}/thumbnail")
async def get_thumbnail(clip_id: str):
    if clip_id not in clips_db:
        raise HTTPException(status_code=404, detail="Clip não encontrado")
    
    clip = clips_db[clip_id]
    if clip["status"] != "completed":
        raise HTTPException(status_code=404, detail="Thumbnail não disponível")
    
    thumbnail_path = CLIPS_DIR / f"{clip_id}.jpg"
    if not thumbnail_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail não encontrada")
    
    return FileResponse(thumbnail_path, media_type="image/jpeg")

@app.get("/clips/{clip_id}/download")
async def download_clip(clip_id: str, request: Request):
    if clip_id not in clips_db:
        raise HTTPException(status_code=404, detail="Clip não encontrado")
    
    clip = clips_db[clip_id]
    if clip["status"] == "processing":
        raise HTTPException(status_code=400, detail="Clip ainda está sendo processado. Aguarde alguns segundos.")
    elif clip["status"] == "pending":
        raise HTTPException(status_code=400, detail="Clip está na fila de processamento. Aguarde.")
    elif clip["status"] == "failed":
        error_msg = clip.get("error", "Erro desconhecido")
        raise HTTPException(status_code=400, detail=f"Falha ao processar clip: {error_msg}")
    elif clip["status"] != "completed":
        raise HTTPException(status_code=400, detail="Clip não está pronto para download")
    
    file_path = Path(clip["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    file_size = file_path.stat().st_size
    range_header = request.headers.get("range")
    
    if range_header:
        range_match = range_header.replace("bytes=", "").split("-")
        start = int(range_match[0]) if range_match[0] else 0
        end = int(range_match[1]) if len(range_match) > 1 and range_match[1] else file_size - 1
        
        def iterfile():
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    chunk_size = min(8192, remaining)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data
        
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
            "Content-Type": "video/mp4",
        }
        return StreamingResponse(iterfile(), status_code=206, headers=headers)
    
    return FileResponse(file_path, media_type="video/mp4", filename=f"clip_{clip_id}.mp4")

@app.patch("/clips/{clip_id}")
async def update_clip(clip_id: str, name: str):
    if clip_id not in clips_db:
        raise HTTPException(status_code=404, detail="Clip não encontrado")
    
    clips_db[clip_id]["name"] = name
    save_db()
    return {"success": True, "name": name}

@app.delete("/clips/{clip_id}")
async def delete_clip(clip_id: str):
    if clip_id not in clips_db:
        raise HTTPException(status_code=404, detail="Clip não encontrado")
    
    clip = clips_db[clip_id]
    if "file_path" in clip:
        file_path = Path(clip["file_path"])
        if file_path.exists():
            file_path.unlink()
    
    del clips_db[clip_id]
    save_db()
    return {"success": True}

@app.get("/clips")
async def list_clips():
    return [
        {
            "id": clip_id,
            "camera_id": clip.get("camera_id", 0),
            "status": clip["status"],
            "name": clip.get("name", f"Clip Camera {clip.get('camera_id', 0)}"),
            "created_at": clip.get("created_at", ""),
            "start_time": clip.get("start_time", ""),
            "end_time": clip.get("end_time", ""),
            "duration": clip.get("duration", 0),
            "file_size": clip.get("file_size", 0),
            "thumbnail_url": f"/clips/{clip_id}/thumbnail" if clip["status"] == "completed" else None
        }
        for clip_id, clip in clips_db.items()
    ]

@app.get("/health")
async def health():
    return {"status": "ok"}
