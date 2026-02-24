import asyncio
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import subprocess

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI(title="Clips Service")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

CLIPS_DIR = Path("/clips")
RECORDINGS_DIR = Path("/recordings")
CLIPS_DIR.mkdir(exist_ok=True)

clips_db = {}

class ClipRequest(BaseModel):
    camera_id: int
    start_time: str
    end_time: str
    format: str = "mp4"
    quality: str = "medium"

class ClipResponse(BaseModel):
    id: str
    status: str
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None

async def create_clip_task(clip_id: str, camera_id: int, start_time: str, end_time: str, quality: str):
    try:
        clips_db[clip_id]["status"] = "processing"
        
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration = int((end_dt - start_dt).total_seconds())
        
        if duration > 300:
            raise Exception("Duração máxima: 5 minutos")
        
        date_str = start_dt.strftime("%Y-%m-%d")
        recording_dir = RECORDINGS_DIR / f"camera_{camera_id}" / date_str
        
        if not recording_dir.exists():
            recording_dir = RECORDINGS_DIR / f"cam_{camera_id}" / date_str
        
        if not recording_dir.exists():
            raise Exception(f"Gravação não encontrada: {recording_dir}")
        
        # Buscar segmentos MP4 de 60s que cobrem o intervalo
        recordings = sorted(recording_dir.glob("*.mp4"))
        if not recordings:
            raise Exception(f"Nenhum arquivo MP4 em {recording_dir}")
        
        # Encontrar segmentos relevantes baseado no timestamp do arquivo
        relevant_files = []
        for rec in recordings:
            try:
                # Parse: HH-MM-SS.mp4 ou timestamp
                parts = rec.stem.split('-')
                if len(parts) >= 3:
                    h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
                    file_dt = start_dt.replace(hour=h, minute=m, second=s)
                    # Arquivo cobre 60s: [file_dt, file_dt+60s]
                    if file_dt <= end_dt and (file_dt + timedelta(seconds=60)) >= start_dt:
                        relevant_files.append((file_dt, rec))
            except:
                continue
        
        if not relevant_files:
            raise Exception("Nenhum segmento encontrado para o intervalo")
        
        relevant_files.sort()
        output_file = CLIPS_DIR / f"{clip_id}.mp4"
        
        if len(relevant_files) == 1:
            # Um único arquivo: cortar diretamente
            file_dt, input_file = relevant_files[0]
            offset = int((start_dt - file_dt).total_seconds())
            
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(max(0, offset)),
                "-i", str(input_file),
                "-t", str(duration),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-movflags", "+faststart",
                "-avoid_negative_ts", "make_zero",
                "-fflags", "+genpts",
                str(output_file)
            ]
        else:
            # Múltiplos arquivos: concatenar e cortar com re-encode
            concat_file = CLIPS_DIR / f"{clip_id}_concat.txt"
            with open(concat_file, 'w') as f:
                for _, rec in relevant_files:
                    f.write(f"file '{rec}'\n")
            
            first_file_dt = relevant_files[0][0]
            offset = int((start_dt - first_file_dt).total_seconds())
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", str(concat_file),
                "-ss", str(max(0, offset)),
                "-t", str(duration),
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-movflags", "+faststart",
                "-avoid_negative_ts", "make_zero",
                "-fflags", "+genpts",
                str(output_file)
            ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"FFmpeg error: {stderr.decode()[-500:]}")
        
        if output_file.exists() and output_file.stat().st_size > 0:
            file_size = output_file.stat().st_size
            clips_db[clip_id].update({
                "status": "completed",
                "file_size": file_size,
                "duration": duration,
                "file_path": str(output_file)
            })
            # Limpar arquivo temporário de concatenação
            concat_file = CLIPS_DIR / f"{clip_id}_concat.txt"
            if concat_file.exists():
                concat_file.unlink()
        else:
            raise Exception("Arquivo vazio ou não criado")
            
    except Exception as e:
        clips_db[clip_id]["status"] = "failed"
        clips_db[clip_id]["error"] = str(e)
        print(f"[CLIP ERROR] {clip_id}: {e}")

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
        "created_at": datetime.now().isoformat()
    }
    
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

@app.get("/clips/{clip_id}/download")
async def download_clip(clip_id: str):
    if clip_id not in clips_db:
        raise HTTPException(status_code=404, detail="Clip não encontrado")
    
    clip = clips_db[clip_id]
    if clip["status"] != "completed":
        raise HTTPException(status_code=400, detail="Clip ainda não está pronto")
    
    file_path = Path(clip["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    return FileResponse(file_path, media_type="video/mp4", filename=f"clip_{clip_id}.mp4")

@app.post("/clips/{clip_id}/publish")
async def publish_clip_to_mediamtx(clip_id: str):
    if clip_id not in clips_db:
        raise HTTPException(status_code=404, detail="Clip não encontrado")
    
    clip = clips_db[clip_id]
    if clip["status"] != "completed":
        raise HTTPException(status_code=400, detail="Clip ainda não está pronto")
    
    file_path = Path(clip["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    stream_name = f"clip_{clip_id}"
    
    # Publica no MediaMTX via FFmpeg em background
    cmd = [
        "ffmpeg", "-re", "-stream_loop", "-1",
        "-i", str(file_path),
        "-c:v", "copy",
        "-c:a", "copy",
        "-f", "rtsp",
        "-rtsp_transport", "tcp",
        f"rtsp://mediamtx:8554/{stream_name}"
    ]
    
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return {
        "status": "publishing",
        "stream_name": stream_name,
        "hls_url": f"http://localhost:8889/{stream_name}/index.m3u8",
        "rtsp_url": f"rtsp://localhost:8554/{stream_name}"
    }

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
    return {"success": True}

@app.get("/clips")
async def list_clips():
    return [
        {
            "id": clip_id,
            "camera_id": clip["camera_id"],
            "status": clip["status"],
            "created_at": clip["created_at"]
        }
        for clip_id, clip in clips_db.items()
    ]

@app.get("/health")
async def health():
    return {"status": "ok"}
