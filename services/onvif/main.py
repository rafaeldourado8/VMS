from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from datetime import datetime
from pathlib import Path
import subprocess
import logging
import httpx

from onvif_client import ONVIFClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("onvif")

app = FastAPI(title="ONVIF Playback Service")

HLS_CACHE = Path("/tmp/hls_onvif")
HLS_CACHE.mkdir(exist_ok=True)

BACKEND_URL = "http://backend:8000"

async def get_camera_info(camera_id: int):
    """Busca informações da câmera do backend."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BACKEND_URL}/api/cameras/{camera_id}/")
        if resp.status_code == 200:
            return resp.json()
        return None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/cameras/{camera_id}/recordings/{date}")
async def list_recordings(camera_id: int, date: str):
    """Lista gravações ONVIF disponíveis na câmera."""
    try:
        camera = await get_camera_info(camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        if not camera.get('onvif_host'):
            raise HTTPException(status_code=400, detail="Camera has no ONVIF config")
        
        dt = datetime.strptime(date, "%Y-%m-%d")
        
        client = ONVIFClient(
            camera['onvif_host'],
            camera.get('onvif_port', 80),
            camera.get('onvif_username', 'admin'),
            camera.get('onvif_password', '')
        )
        recordings = await client.get_recordings(dt, dt)
        
        return [{
            'start': rec['earliest'],
            'end': rec['latest'],
            'type': 'onvif',
            'token': rec['token']
        } for rec in recordings]
    
    except Exception as e:
        logger.error(f"Error listing recordings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/playback/{camera_id}/{date}/{time}.m3u8")
async def playback_manifest(camera_id: int, date: str, time: str):
    """Gera manifest HLS do playback ONVIF."""
    try:
        camera = await get_camera_info(camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        if not camera.get('onvif_host'):
            raise HTTPException(status_code=400, detail="Camera has no ONVIF config")
        
        dt = datetime.strptime(f"{date} {time.replace('-', ':')}", "%Y-%m-%d %H:%M")
        
        client = ONVIFClient(
            camera['onvif_host'],
            camera.get('onvif_port', 80),
            camera.get('onvif_username', 'admin'),
            camera.get('onvif_password', '')
        )
        recordings = await client.get_recordings(dt, dt)
        
        if not recordings:
            raise HTTPException(status_code=404, detail="No recordings found")
        
        recording_token = recordings[0]['token']
        replay_uri = await client.get_replay_uri(recording_token, dt)
        
        if not replay_uri:
            raise HTTPException(status_code=500, detail="Failed to get replay URI")
        
        # Gerar HLS
        cache_key = f"cam{camera_id}_{date}_{time}"
        manifest_path = HLS_CACHE / f"{cache_key}.m3u8"
        
        if not manifest_path.exists():
            cmd = [
                "ffmpeg", "-y",
                "-rtsp_transport", "tcp",
                "-i", replay_uri,
                "-t", "300",
                "-c", "copy",
                "-f", "hls",
                "-hls_time", "2",
                "-hls_list_size", "0",
                "-hls_segment_filename", str(HLS_CACHE / f"{cache_key}_%03d.ts"),
                str(manifest_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode != 0:
                raise HTTPException(status_code=500, detail="FFmpeg failed")
        
        with open(manifest_path, 'r') as f:
            content = f.read()
        
        return StreamingResponse(iter([content]), media_type='application/vnd.apple.mpegurl')
    
    except Exception as e:
        logger.error(f"Error generating manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/playback/{camera_id}/{date}/{time}_{segment}")
async def playback_segment(camera_id: int, date: str, time: str, segment: str):
    """Serve segmento HLS."""
    cache_key = f"cam{camera_id}_{date}_{time}"
    segment_path = HLS_CACHE / f"{cache_key}_{segment}"
    
    if not segment_path.exists():
        raise HTTPException(status_code=404, detail="Segment not found")
    
    return FileResponse(segment_path, media_type='video/mp2t')
