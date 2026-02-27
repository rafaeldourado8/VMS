import asyncio
import httpx
import logging
from pathlib import Path
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cleanup")

RECORDINGS_DIR = Path("/recordings")

async def get_active_cameras():
    """Busca IDs de câmeras ativas no backend"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get("http://backend:8000/api/cameras/recorder/")
            resp.raise_for_status()
            cameras = resp.json()
            if isinstance(cameras, list):
                return {cam["id"] for cam in cameras if isinstance(cam, dict)}
            return set()
    except Exception as e:
        logger.error(f"Erro ao buscar câmeras: {e}")
        return set()

async def cleanup_orphan_recordings():
    """Remove gravações de câmeras que não existem mais"""
    logger.info("Iniciando limpeza de gravações órfãs...")
    
    active_cameras = await get_active_cameras()
    if not active_cameras:
        logger.warning("Nenhuma câmera ativa encontrada, abortando limpeza")
        return
    
    logger.info(f"Câmeras ativas: {sorted(active_cameras)}")
    
    removed_count = 0
    removed_size = 0
    
    for camera_dir in RECORDINGS_DIR.glob("camera_*"):
        if not camera_dir.is_dir():
            continue
        
        try:
            camera_id = int(camera_dir.name.replace("camera_", ""))
            
            if camera_id not in active_cameras:
                # Calcular tamanho antes de remover
                size = sum(f.stat().st_size for f in camera_dir.rglob("*") if f.is_file())
                
                logger.info(f"Removendo gravações da câmera {camera_id} ({size / 1024 / 1024:.1f} MB)")
                shutil.rmtree(camera_dir)
                
                removed_count += 1
                removed_size += size
        except Exception as e:
            logger.error(f"Erro ao processar {camera_dir}: {e}")
    
    if removed_count > 0:
        logger.info(f"✅ Removidas {removed_count} pastas ({removed_size / 1024 / 1024:.1f} MB)")
    else:
        logger.info("Nenhuma gravação órfã encontrada")

async def main():
    while True:
        await cleanup_orphan_recordings()
        await asyncio.sleep(3600)  # Executar a cada 1 hora

if __name__ == "__main__":
    asyncio.run(main())
