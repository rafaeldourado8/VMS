#!/usr/bin/env python3
"""Monitor MediaMTX crashes e reprovisiona câmeras automaticamente."""

import asyncio
import logging
import httpx
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mediamtx_monitor")

MEDIAMTX_API = "http://mediamtx:9997"
STREAMING_API = "http://streaming:8001"
AUTH = ("mediamtx_api_user", "GtV!sionMed1aMTX$2025")
CHECK_INTERVAL = 30  # segundos

async def check_mediamtx_health():
    """Verifica se MediaMTX está respondendo."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{MEDIAMTX_API}/v3/config/global/get", auth=AUTH)
            return resp.status_code == 200
    except:
        return False

async def get_provisioned_cameras():
    """Lista câmeras que devem estar provisionadas."""
    # TODO: Buscar do banco de dados
    return [
        {"camera_id": 1, "rtsp_url": "rtsp://admin:Camerite123@45.236.226.70:6044/cam/realmonitor?channel=1&subtype=0"},
        {"camera_id": 2, "rtsp_url": "rtsp://admin:Camerite123@45.236.226.70:6045/cam/realmonitor?channel=1&subtype=0"},
        {"camera_id": 3, "rtsp_url": "rtsp://admin:Camerite@186.226.193.111:602/h264/ch1/main/av_stream"},
    ]

async def reprovision_cameras():
    """Reprovisiona todas as câmeras após crash."""
    cameras = await get_provisioned_cameras()
    logger.info(f"🔄 Reprovisionando {len(cameras)} câmeras...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for cam in cameras:
            try:
                resp = await client.post(
                    f"{STREAMING_API}/cameras/provision",
                    json={
                        "camera_id": cam["camera_id"],
                        "rtsp_url": cam["rtsp_url"],
                        "name": f"Camera {cam['camera_id']}",
                        "enabled": True,
                        "on_demand": False
                    }
                )
                if resp.status_code == 200:
                    logger.info(f"✅ cam_{cam['camera_id']} reprovisionada")
                else:
                    logger.error(f"❌ cam_{cam['camera_id']} falhou: {resp.text}")
            except Exception as e:
                logger.error(f"❌ Erro ao reprovisionar cam_{cam['camera_id']}: {e}")
            
            await asyncio.sleep(2)

async def monitor_loop():
    """Loop principal de monitoramento."""
    was_healthy = True
    
    while True:
        try:
            is_healthy = await check_mediamtx_health()
            
            if not is_healthy and was_healthy:
                logger.error("🔴 MediaMTX CRASH DETECTADO!")
                logger.info("⏳ Aguardando MediaMTX reiniciar...")
                await asyncio.sleep(10)
                
                # Aguardar MediaMTX voltar
                for i in range(30):
                    if await check_mediamtx_health():
                        logger.info("✅ MediaMTX voltou online")
                        await reprovision_cameras()
                        break
                    await asyncio.sleep(2)
            
            elif is_healthy and not was_healthy:
                logger.info("✅ MediaMTX recuperado")
            
            was_healthy = is_healthy
            
        except Exception as e:
            logger.error(f"Erro no monitor: {e}")
        
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    logger.info("🚀 Iniciando monitor de crashes do MediaMTX...")
    asyncio.run(monitor_loop())
