import asyncio
import subprocess
import httpx
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recorder")

class Recorder:
    def __init__(self, camera_id: int, rtsp_url: str):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.process = None
        
    async def start(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.now().strftime("%H-%M-%S")
        output_dir = f"/recordings/cam_{self.camera_id}/{date_str}"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_path = f"{output_dir}/{time_str}.mp4"
        
        cmd = [
            "ffmpeg", "-y",
            "-rtsp_transport", "tcp",
            "-i", self.rtsp_url,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "28",
            "-maxrate", "2M",
            "-bufsize", "4M",
            "-c:a", "aac",
            "-b:a", "64k",
            "-f", "segment",
            "-segment_time", "86400",
            "-segment_format", "mp4",
            "-reset_timestamps", "1",
            "-strftime", "1",
            output_path
        ]
        
        self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Gravacao iniciada: cam_{self.camera_id} (bitrate reduzido)")
        
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
                recorder = Recorder(cam_id, cam_data["stream_url"])
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
