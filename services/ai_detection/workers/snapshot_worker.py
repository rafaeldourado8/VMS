"""
Snapshot Worker - Gera snapshots assíncronos das câmeras
Extrai 1 frame a cada 30 segundos e publica no Redis via SnapshotCache
"""
import asyncio
import logging
import os
from typing import Dict, Optional
from redis import Redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SnapshotCache:
    """Cache de snapshots no Redis"""
    def __init__(self, redis: Redis, ttl: int = 60):
        self.redis = redis
        self.ttl = ttl
    
    def set(self, camera_id: str, image_bytes: bytes):
        key = f"snapshot:{camera_id}"
        self.redis.setex(key, self.ttl, image_bytes)
        logger.debug(f"Snapshot salvo para camera {camera_id}")


class SnapshotWorker:
    """Worker para gerar snapshots das câmeras"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = Redis.from_url(redis_url, decode_responses=False)
        self.cache = SnapshotCache(self.redis, ttl=60)
        self.active_cameras: Dict[str, str] = {}
        self.running = False
    
    def add_camera(self, camera_id: str, rtsp_url: str):
        """Adiciona câmera para monitoramento"""
        self.active_cameras[camera_id] = rtsp_url
        logger.info(f"Câmera {camera_id} adicionada ao snapshot worker")
    
    def remove_camera(self, camera_id: str):
        """Remove câmera do monitoramento"""
        if camera_id in self.active_cameras:
            del self.active_cameras[camera_id]
            logger.info(f"Câmera {camera_id} removida do snapshot worker")
    
    async def extract_snapshot(self, camera_id: str, rtsp_url: str) -> Optional[bytes]:
        """Extrai um único frame da câmera usando ffmpeg"""
        cmd = [
            "ffmpeg",
            "-rtsp_transport", "tcp",
            "-i", rtsp_url,
            "-frames:v", "1",
            "-f", "image2pipe",
            "-vcodec", "mjpeg",
            "-q:v", "5",
            "-"
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )
            
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=10.0)
            
            if stdout and len(stdout) > 0:
                return stdout
            
        except asyncio.TimeoutError:
            logger.warning(f"Timeout ao extrair snapshot da câmera {camera_id}")
        except Exception as e:
            logger.error(f"Erro ao extrair snapshot da câmera {camera_id}: {e}")
        
        return None
    
    async def process_camera(self, camera_id: str, rtsp_url: str):
        """Processa uma câmera gerando snapshots a cada 30 segundos"""
        logger.info(f"Iniciando processamento de snapshots para câmera {camera_id}")
        
        while self.running and camera_id in self.active_cameras:
            try:
                snapshot = await self.extract_snapshot(camera_id, rtsp_url)
                
                if snapshot:
                    self.cache.set(camera_id, snapshot)
                    logger.info(f"Snapshot gerado para câmera {camera_id} ({len(snapshot)} bytes)")
                else:
                    logger.warning(f"Falha ao gerar snapshot para câmera {camera_id}")
                
            except Exception as e:
                logger.error(f"Erro ao processar câmera {camera_id}: {e}")
            
            await asyncio.sleep(30)
        
        logger.info(f"Processamento de snapshots finalizado para câmera {camera_id}")
    
    async def start(self):
        """Inicia o worker"""
        self.running = True
        logger.info("Snapshot Worker iniciado")
        
        tasks = []
        for camera_id, rtsp_url in self.active_cameras.items():
            task = asyncio.create_task(self.process_camera(camera_id, rtsp_url))
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stop(self):
        """Para o worker"""
        self.running = False
        logger.info("Snapshot Worker parado")


async def main():
    """Função principal para testes"""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    worker = SnapshotWorker(redis_url)
    
    # Exemplo: adicionar câmeras
    worker.add_camera("1", "rtsp://example.com/stream1")
    worker.add_camera("2", "rtsp://example.com/stream2")
    
    try:
        await worker.start()
    except KeyboardInterrupt:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
