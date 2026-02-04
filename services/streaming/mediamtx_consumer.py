import asyncio
import logging
import httpx
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class MediaMTXEventConsumer:
    """Consome eventos do MediaMTX para iniciar/parar gravações."""
    
    def __init__(self, mediamtx_api_url: str, auth: tuple):
        self.api_url = mediamtx_api_url
        self.auth = auth
        self.client = httpx.AsyncClient(timeout=10.0)
        self.active_recordings = {}  # {stream_path: recording_id}
    
    async def start_recording(self, stream_path: str, camera_id: int) -> bool:
        """Inicia gravação no MediaMTX via API."""
        try:
            config = {
                "record": True,
                "recordPath": f"/recordings/{stream_path}/%Y-%m-%d_%H-%M-%S-%f",
                "recordFormat": "fmp4",
                "recordPartDuration": "4s",
                "recordSegmentDuration": "30m"
            }
            
            resp = await self.client.patch(
                f"{self.api_url}/v3/config/paths/patch/{stream_path}",
                json=config,
                auth=self.auth
            )
            
            if resp.status_code in [200, 204]:
                logger.info(f"✅ Gravação iniciada: {stream_path}")
                
                # Cria registro no Django
                from apps.cameras.models_recording import Recording
                from apps.cameras.models import Camera
                
                camera = await Camera.objects.aget(id=camera_id)
                recording = await Recording.objects.acreate(
                    camera=camera,
                    video_path=f"/recordings/{stream_path}/",
                    started_at=datetime.now()
                )
                self.active_recordings[stream_path] = recording.id
                return True
            
            return False
        except Exception as e:
            logger.error(f"Erro ao iniciar gravação {stream_path}: {e}")
            return False
    
    async def stop_recording(self, stream_path: str) -> bool:
        """Para gravação e atualiza registro."""
        try:
            config = {"record": False}
            resp = await self.client.patch(
                f"{self.api_url}/v3/config/paths/patch/{stream_path}",
                json=config,
                auth=self.auth
            )
            
            if resp.status_code in [200, 204]:
                logger.info(f"⏹️ Gravação parada: {stream_path}")
                
                # Atualiza registro
                if stream_path in self.active_recordings:
                    from apps.cameras.models_recording import Recording
                    recording_id = self.active_recordings.pop(stream_path)
                    recording = await Recording.objects.aget(id=recording_id)
                    recording.ended_at = datetime.now()
                    await recording.asave()
                
                return True
            return False
        except Exception as e:
            logger.error(f"Erro ao parar gravação {stream_path}: {e}")
            return False
    
    async def poll_events(self):
        """Monitora eventos de HLS (stream ready/closed)."""
        while True:
            try:
                resp = await self.client.get(f"{self.api_url}/v3/paths/list", auth=self.auth)
                paths = resp.json().get("items", [])
                
                for path in paths:
                    name = path.get("name", "")
                    if not name.startswith("cam_"):
                        continue
                    
                    ready = path.get("ready", False)
                    readers = len(path.get("readers", []))
                    
                    # Inicia gravação quando HLS está ativo
                    if ready and readers > 0 and name not in self.active_recordings:
                        camera_id = int(name.replace("cam_", ""))
                        await self.start_recording(name, camera_id)
                    
                    # Para gravação quando HLS fecha
                    elif (not ready or readers == 0) and name in self.active_recordings:
                        await self.stop_recording(name)
                
                await asyncio.sleep(5)  # Poll a cada 5s
            except Exception as e:
                logger.error(f"Erro no poll de eventos: {e}")
                await asyncio.sleep(10)
