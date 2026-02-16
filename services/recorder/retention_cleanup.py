"""
Servico de Limpeza de Retencao
Executa a cada 1 hora e deleta gravacoes antigas baseado na politica de retencao de cada camera
"""
import asyncio
import httpx
import logging
from datetime import datetime, timedelta
from pathlib import Path
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retention_cleanup")

RECORDINGS_BASE = Path("/recordings")
CHECK_INTERVAL = 3600  # 1 hora

async def get_cameras_retention():
    """Busca politica de retencao de todas as cameras"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get("http://backend:8000/api/cameras/recorder/")
            resp.raise_for_status()
            cameras = resp.json()
            
            # Mapear camera_id -> retention_days
            retention_map = {}
            for cam in cameras:
                if isinstance(cam, dict):
                    retention_map[cam["id"]] = cam.get("recording_retention_days", 30)
            
            return retention_map
    except Exception as e:
        logger.error(f"Erro ao buscar cameras: {e}")
        return {}

async def cleanup_old_recordings():
    """Remove gravacoes antigas baseado na politica de retencao (FIFO)"""
    logger.info("="*60)
    logger.info("LIMPEZA AUTOMATICA DE RETENCAO (FIFO)")
    logger.info("="*60)
    
    retention_map = await get_cameras_retention()
    if not retention_map:
        logger.warning("Nenhuma camera encontrada")
        return
    
    today = datetime.now().date()
    total_deleted = 0
    total_size = 0
    
    for camera_folder in RECORDINGS_BASE.glob("camera_*"):
        if not camera_folder.is_dir():
            continue
        
        try:
            camera_id = int(camera_folder.name.split("_")[1])
        except (IndexError, ValueError):
            continue
        
        retention_days = retention_map.get(camera_id, 30)
        cutoff_date = today - timedelta(days=retention_days)
        
        logger.info(f"Camera {camera_id}: Politica {retention_days} dias | Deletar antes de {cutoff_date}")
        
        deleted_folders = 0
        for date_folder in sorted(camera_folder.iterdir()):
            if not date_folder.is_dir():
                continue
            
            try:
                folder_date = datetime.strptime(date_folder.name, "%Y-%m-%d").date()
            except ValueError:
                continue
            
            # FIFO: Deleta gravacoes mais antigas que a politica
            if folder_date < cutoff_date:
                files = list(date_folder.glob("*.mp4"))
                folder_size = sum(f.stat().st_size for f in files)
                
                logger.info(f"  [DELETANDO] {date_folder.name}: {len(files)} arquivos, {folder_size/1024/1024:.2f} MB")
                
                shutil.rmtree(date_folder)
                total_deleted += len(files)
                total_size += folder_size
                deleted_folders += 1
        
        if deleted_folders == 0:
            logger.info(f"  [OK] Nenhuma gravacao antiga para deletar")
    
    logger.info("="*60)
    logger.info(f"TOTAL: {total_deleted} arquivos deletados | {total_size/1024/1024:.2f} MB liberados")
    logger.info("="*60)

async def main():
    logger.info("="*60)
    logger.info("SERVICO DE RETENCAO AUTOMATICA (FIFO)")
    logger.info("="*60)
    logger.info(f"Verificacao ciclica a cada {CHECK_INTERVAL/3600:.1f} hora(s)")
    logger.info("Politica: Deleta gravacoes mais antigas que o periodo configurado")
    logger.info("  - 7 dias: Mantem ultimos 7 dias, deleta anteriores")
    logger.info("  - 15 dias: Mantem ultimos 15 dias, deleta anteriores")
    logger.info("  - 30 dias: Mantem ultimos 30 dias, deleta anteriores")
    logger.info("="*60)
    
    while True:
        try:
            await cleanup_old_recordings()
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")
        
        logger.info(f"Proxima verificacao em {CHECK_INTERVAL/3600:.1f} hora(s)...\n")
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
