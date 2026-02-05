from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import subprocess
import httpx

app = FastAPI(title="Recording Service")

class RecordingStatus(BaseModel):
    camera_id: int
    date: str
    files: list[dict]
    total_size_mb: float

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/recordings/{camera_id}")
async def get_recordings(camera_id: int, date: str = None):
    """Lista gravações de uma câmera"""
    base = Path(f"/recordings/cam_{camera_id}")
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    path = base / target_date
    
    if not path.exists():
        raise HTTPException(404, "Gravações não encontradas")
    
    files = []
    total_size = 0
    
    for f in sorted(path.glob("*.mp4")):
        size = f.stat().st_size
        total_size += size
        files.append({
            "name": f.name,
            "size_mb": round(size / 1024 / 1024, 2),
            "path": str(f)
        })
    
    return {
        "camera_id": camera_id,
        "date": target_date,
        "files": files,
        "total_size_mb": round(total_size / 1024 / 1024, 2)
    }

@app.post("/recordings/{camera_id}/validate")
async def validate_recording(camera_id: int, date: str = None):
    """Valida integridade das gravações"""
    base = Path(f"/recordings/cam_{camera_id}")
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    path = base / target_date
    
    if not path.exists():
        raise HTTPException(404, "Gravações não encontradas")
    
    results = []
    for f in sorted(path.glob("*.mp4")):
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", 
                 "format=duration:stream=codec_name", "-of", "csv=p=0", str(f)],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                results.append({
                    "file": f.name,
                    "valid": True,
                    "codec": parts[0] if len(parts) > 0 else "unknown",
                    "duration_min": round(float(parts[1]) / 60, 1) if len(parts) > 1 else 0
                })
            else:
                results.append({"file": f.name, "valid": False})
        except:
            results.append({"file": f.name, "valid": False})
    
    return {"camera_id": camera_id, "date": target_date, "results": results}

@app.post("/recordings/{camera_id}/notify")
async def notify_backend(camera_id: int, date: str, file: str):
    """Notifica Django backend sobre nova gravação"""
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://backend:8000/api/recordings/",
            json={"camera_id": camera_id, "date": date, "file": file}
        )
    return {"status": "notified"}
