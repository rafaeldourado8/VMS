import os
import logging
from typing import List, Dict, Any, Optional
import aiohttp
import asyncio
from datetime import datetime
from config import settings

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = (base_url or settings.backend_url).rstrip('/')
        self.api_key = api_key or settings.admin_api_key or os.getenv("ADMIN_API_KEY")
        self.headers = {"X-API-Key": self.api_key} if self.api_key else {}
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def get_cameras(self) -> List[Dict[str, Any]]:
        """Busca câmeras no endpoint real: /api/cameras/"""
        try:
            await self._ensure_session()
            async with self.session.get(f"{self.base_url}/api/cameras/") as resp:
                if resp.status == 200:
                    return await resp.json()
                logger.error(f"Erro ao buscar câmeras: {resp.status}")
                return []
        except Exception as e:
            logger.error(f"Falha de conexão: {e}")
            return []

    async def send_sighting(self, plate: str, camera_id: int, vehicle_type: str = "unknown", 
                             confidence: float = 0.0, image_url: str = None) -> bool:
        """Envia para o endpoint real de ingestão: /api/ingest/"""
        try:
            await self._ensure_session()
            # Mapeamento exato para o IngestDeteccaoSerializer do Django
            payload = {
                "camera_id": camera_id,
                "timestamp": datetime.utcnow().isoformat(),
                "plate": plate,
                "confidence": confidence,
                "vehicle_type": vehicle_type,
                "image_url": image_url
            }
            
            async with self.session.post(f"{self.base_url}/api/ingest/", json=payload) as resp:
                if resp.status == 201:
                    logger.info(f"Deteção enviada: {plate}")
                    return True
                logger.error(f"Erro na ingestão ({resp.status}): {await resp.text()}")
                return False
        except Exception as e:
            logger.error(f"Erro ao enviar sighting: {e}")
            return False

    async def close(self):
        if self.session: await self.session.close()