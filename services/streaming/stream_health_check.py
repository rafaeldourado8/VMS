#!/usr/bin/env python3
"""
Health Check e Auto-Recovery para Streaming
Verifica inconsistências entre Redis/DB e MediaMTX e corrige automaticamente
"""

import asyncio
import logging
import httpx
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stream_health")

STREAMING_API = "http://streaming:8001"
BACKEND_API = "http://backend:8000"
CHECK_INTERVAL = 60  # segundos

async def get_cameras_from_backend():
    """Busca câmeras ativas do backend."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{BACKEND_API}/api/cameras/for_recorder/")
            if resp.status_code == 200:
                return resp.json()
            return []
    except Exception as e:
        logger.error(f"Erro ao buscar câmeras do backend: {e}")
        return []

async def get_streams_from_mediamtx():
    """Lista streams ativos no MediaMTX."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{STREAMING_API}/stats")
            if resp.status_code == 200:
                data = resp.json()
                return {s['path']: s for s in data.get('streams', [])}
            return {}
    except Exception as e:
        logger.error(f"Erro ao buscar streams: {e}")
        return {}

async def provision_camera(camera_id: int, rtsp_url: str, name: str):
    """Provisiona câmera no streaming service."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{STREAMING_API}/cameras/provision",
                json={
                    "camera_id": camera_id,
                    "rtsp_url": rtsp_url,
                    "name": name,
                    "enabled": True,
                    "on_demand": True
                }
            )
            return resp.status_code == 200
    except Exception as e:
        logger.error(f"Erro ao provisionar cam_{camera_id}: {e}")
        return False

async def health_check_loop():
    """Loop principal de verificação."""
    logger.info("🏥 Iniciando health check de streaming...")
    
    while True:
        try:
            cameras = await get_cameras_from_backend()
            streams = await get_streams_from_mediamtx()
            
            missing = []
            for cam in cameras:
                stream_path = f"cam_{cam['id']}"
                if stream_path not in streams:
                    missing.append(cam)
            
            if missing:
                logger.warning(f"⚠️ {len(missing)} câmeras fora de sincronia")
                for cam in missing:
                    logger.info(f"🔄 Reprovisionando cam_{cam['id']}...")
                    success = await provision_camera(
                        cam['id'],
                        cam['stream_url'],
                        cam['name']
                    )
                    if success:
                        logger.info(f"✅ cam_{cam['id']} restaurada")
                    else:
                        logger.error(f"❌ Falha ao restaurar cam_{cam['id']}")
                    await asyncio.sleep(2)
            else:
                logger.info(f"✅ Todas as {len(cameras)} câmeras sincronizadas")
            
        except Exception as e:
            logger.error(f"Erro no health check: {e}")
        
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(health_check_loop())
