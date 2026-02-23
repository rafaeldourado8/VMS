import asyncio
import subprocess
import httpx
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recorder")

class Recorder:
    def __init__(self, camera_id: int, rtsp_url: str, timezone: str = "America/Sao_Paulo"):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.timezone = timezone
        self.process = None
        
    async def start(self):
        tz = ZoneInfo(self.timezone)
        date_str = datetime.now(tz).strftime("%Y-%m-%d")
        output_dir = f"/recordings/camera_{self.camera_id}/{date_str}"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = f"{output_dir}/%H-%M-%S.mp4"
        
        cmd = [
            "ffmpeg", "-y",
            "-rtsp_transport", "tcp",
            "-timeout", "5000000",
            "-i", self.rtsp_url,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-g", "60",
            "-an",
            "-avoid_negative_ts", "make_zero",
            "-fflags", "+genpts",
            "-movflags", "+faststart+frag_keyframe+empty_moov",
            "-f", "segment",
            "-segment_time", "60",
            "-segment_format", "mp4",
            "-reset_timestamps", "1",
            "-strftime", "1",
            output_path
        ]
        
        self.process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True
        )
        logger.info(f"Gravacao iniciada: camera_{self.camera_id} - CRF 20, preset medium, 60s segments")
        
    async def monitor(self):
        while True:
            if self.process and self.process.poll() is not None:
                logger.warning(f"Processo morreu, reiniciando cam_{self.camera_id}")
                await self.start()
            await asyncio.sleep(60)
    
    def stop(self):
        if self.process:
            self.process.terminate()
            logger.info(f"Gravacao parada: cam_{self.camera_id}")

async def sync_cameras():
    """Sincroniza cameras do backend e retorna dict de recorders ativos"""
    client = httpx.AsyncClient(timeout=30.0)
    
    try:
        resp = await client.get("http://backend:8000/api/cameras/recorder/")
        resp.raise_for_status()
        data = resp.json()
        
        if isinstance(data, dict) and 'error' in data:
            logger.error(f"Backend error: {data['error']}")
            cameras = data.get('cameras', [])
        elif isinstance(data, list):
            cameras = data
        else:
            logger.error(f"Resposta invalida: {type(data)}")
            return {}
        
        return {cam["id"]: cam for cam in cameras if isinstance(cam, dict) and cam.get("status") == "online"}
    except Exception as e:
        logger.error(f"Erro ao buscar cameras: {e}")
        return {}
    finally:
        await client.aclose()

async def main():
    recorders = {}
    
    while True:
        cameras = await sync_cameras()
        
        # Remover recorders de cameras que nao existem mais
        for cam_id in list(recorders.keys()):
            if cam_id not in cameras:
                logger.info(f"Parando gravacao: cam_{cam_id}")
                if recorders[cam_id].process:
                    recorders[cam_id].process.terminate()
                del recorders[cam_id]
        
        # Adicionar recorders para novas cameras
        for cam_id, cam_data in cameras.items():
            if cam_id not in recorders:
                logger.info(f"Iniciando gravacao: cam_{cam_id}")
                timezone = cam_data.get("timezone", "America/Sao_Paulo")
                recorder = Recorder(cam_id, cam_data["stream_url"], timezone)
                await recorder.start()
                recorders[cam_id] = recorder
        
        # Monitorar processos
        for recorder in recorders.values():
            if recorder.process and recorder.process.poll() is not None:
                logger.warning(f"Processo morreu, reiniciando cam_{recorder.camera_id}")
                await recorder.start()
        
        logger.info(f"Gravando {len(recorders)} cameras")
        await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())
