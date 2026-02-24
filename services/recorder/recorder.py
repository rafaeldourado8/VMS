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
        self.mediamtx_url = f"rtsp://mediamtx:8554/cam_{camera_id}"
        self.last_file_time = None
        
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
            "-i", self.mediamtx_url,
            "-c:v", "copy",
            "-an",
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
        logger.info(f"Gravacao iniciada: camera_{self.camera_id} - codec copy")
        logger.info(f"FFmpeg PID: {self.process.pid}, URL: {self.mediamtx_url}")
        
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
        
        # Monitorar e reiniciar processos mortos ou travados
        for recorder in recorders.values():
            # Verifica se processo morreu
            if recorder.process and recorder.process.poll() is not None:
                returncode = recorder.process.returncode
                stderr_output = ""
                if recorder.process.stderr:
                    try:
                        stderr_lines = recorder.process.stderr.readlines()
                        stderr_output = ''.join(stderr_lines[-20:])
                    except:
                        pass
                
                logger.error(f"FFmpeg cam_{recorder.camera_id} morreu (exit {returncode})")
                if stderr_output:
                    logger.error(f"Stderr: {stderr_output}")
                
                await asyncio.sleep(5)
                await recorder.start()
                continue
            
            # Watchdog: verifica se está criando arquivos
            if recorder.process:
                try:
                    tz = ZoneInfo(recorder.timezone)
                    date_str = datetime.now(tz).strftime("%Y-%m-%d")
                    output_dir = Path(f"/recordings/camera_{recorder.camera_id}/{date_str}")
                    
                    if output_dir.exists():
                        mp4_files = sorted(output_dir.glob("*.mp4"))
                        if mp4_files:
                            latest_file = mp4_files[-1]
                            file_mtime = latest_file.stat().st_mtime
                            
                            # Se último arquivo tem mais de 65s, FFmpeg travou
                            if datetime.now().timestamp() - file_mtime > 65:
                                logger.warning(f"FFmpeg cam_{recorder.camera_id} travado (sem arquivos há 65s), reiniciando")
                                recorder.process.kill()
                                await asyncio.sleep(2)
                                await recorder.start()
                except Exception as e:
                    logger.error(f"Erro no watchdog cam_{recorder.camera_id}: {e}")
        
        logger.info(f"Gravando {len(recorders)} cameras")
        await asyncio.sleep(10)  # Verifica a cada 10s

if __name__ == "__main__":
    asyncio.run(main())
