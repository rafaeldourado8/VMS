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
        
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        duration = int((end_dt - start_dt).total_seconds())
        
        if duration > 300:
            raise Exception("Duração máxima: 5 minutos")
        
        date_str = start_dt.strftime("%Y-%m-%d")
        recording_dir = RECORDINGS_DIR / f"cam_{camera_id}" / date_str
        
        if not recording_dir.exists():
            raise Exception("Gravação não encontrada")
        
        recordings = sorted(recording_dir.glob("*.mp4"))
        if not recordings:
            raise Exception("Nenhum arquivo de gravação")
        
        input_file = recordings[0]
        output_file = CLIPS_DIR / f"{clip_id}.mp4"
        
        start_offset = start_dt.strftime("%H:%M:%S")
        
        quality_map = {
            "low": "28",
            "medium": "23",
            "high": "18"
        }
        crf = quality_map.get(quality, "23")
        
        cmd = [
            "ffmpeg", "-y",
            "-ss", start_offset,
            "-i", str(input_file),
            "-t", str(duration),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", crf,
            "-c:a", "aac",
            "-movflags", "+faststart",
            str(output_file)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        if output_file.exists():
            file_size = output_file.stat().st_size
            clips_db[clip_id].update({
                "status": "completed",
                "file_size": file_size,
                "duration": duration,
                "file_path": str(output_file)
            })
        else:
            raise Exception("Falha ao criar clip")
            
    except Exception as e:
        clips_db[clip_id]["status"] = "failed"
        clips_db[clip_id]["error"] = str(e)

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
