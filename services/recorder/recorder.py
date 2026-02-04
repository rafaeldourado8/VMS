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
        logger.info(f"📹 Gravação iniciada: cam_{self.camera_id} (bitrate reduzido)")
        
    async def monitor(self):
        while True:
            if self.process and self.process.poll() is not None:
                logger.warning(f"Processo morreu, reiniciando cam_{self.camera_id}")
                await self.start()
            await asyncio.sleep(60)

async def main():
    client = httpx.AsyncClient()
    
    try:
        resp = await client.get("http://backend:8000/api/cameras/")
        
        if resp.status_code == 401:
            logger.error("❌ Não autorizado - Backend requer autenticação")
            return
        
        resp.raise_for_status()
        cameras = resp.json()
        
        if not isinstance(cameras, list):
            logger.error(f"❌ Resposta inválida do backend: {cameras}")
            return
        
        tasks = []
        for cam in cameras:
            if isinstance(cam, dict) and cam.get("enabled"):
                recorder = Recorder(cam["id"], cam["stream_url"])
                await recorder.start()
                tasks.append(recorder.monitor())
        
        if not tasks:
            logger.warning("⚠️ Nenhuma câmera habilitada encontrada")
            return
        
        await asyncio.gather(*tasks)
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar gravação: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
