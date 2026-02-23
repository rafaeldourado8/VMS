"""
Servico de Limpeza de Retencao
Executa a cada 1 hora e deleta gravacoes antigas baseado na politica de retencao de cada camera
NAO DELETA CLIPS PROTEGIDOS
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

async def get_protected_clips():
    """Busca lista de arquivos de clips protegidos do banco"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get("http://backend:8000/api/clips/protected-files/")
            if resp.status_code == 200:
                data = resp.json()
                return set(data.get('protected_files', []))
    except Exception as e:
        logger.error(f"Erro ao buscar clips protegidos: {e}")
    return set()

async def cleanup_old_recordings():
    """Remove gravacoes antigas baseado na politica de retencao (FIFO)"""
    logger.info("="*60)
    logger.info("LIMPEZA AUTOMATICA DE RETENCAO (FIFO)")
    logger.info("="*60)
    
    if not RECORDINGS_BASE.exists():
        logger.warning(f"Diretorio {RECORDINGS_BASE} nao existe")
        return
    
    retention_map = await get_cameras_retention()
    if not retention_map:
        logger.warning("Nenhuma camera encontrada, usando retencao padrao de 7 dias")
        retention_map = {}
    
    # Buscar clips protegidos
    protected_files = await get_protected_clips()
    logger.info(f"Clips protegidos: {len(protected_files)} arquivos")
    
    today = datetime.now().date()
    total_deleted = 0
    total_size = 0
    total_protected = 0
    cameras_processed = 0
    
    # Processar ambos formatos: camera_ e cam_
    for camera_folder in list(RECORDINGS_BASE.glob("camera_*")) + list(RECORDINGS_BASE.glob("cam_*")):
        if not camera_folder.is_dir():
            continue
        
        try:
            camera_id = int(camera_folder.name.split("_")[1])
        except (IndexError, ValueError):
            logger.warning(f"Pasta invalida: {camera_folder.name}")
            continue
        
        retention_days = retention_map.get(camera_id, 7)  # Padrao 7 dias
        cutoff_date = today - timedelta(days=retention_days)
        
        logger.info(f"Camera {camera_id}: Retencao {retention_days} dias | Deletar antes de {cutoff_date}")
        
        deleted_folders = 0
        date_folders = sorted([d for d in camera_folder.iterdir() if d.is_dir()])
        
        for date_folder in date_folders:
            try:
                folder_date = datetime.strptime(date_folder.name, "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"  Pasta com formato invalido: {date_folder.name}")
                continue
            
            # FIFO: Deleta gravacoes mais antigas que a politica
            if folder_date < cutoff_date:
                files = list(date_folder.glob("*.mp4"))
                folder_size = sum(f.stat().st_size for f in files if f.exists())
                
                # Verificar clips protegidos
                protected_in_folder = [f for f in files if str(f) in protected_files]
                if protected_in_folder:
                    logger.info(f"  [PROTEGIDO] {date_folder.name}: {len(protected_in_folder)} clips protegidos, mantendo pasta")
                    total_protected += len(protected_in_folder)
                    continue
                
                logger.info(f"  [DELETANDO] {date_folder.name}: {len(files)} arquivos, {folder_size/1024/1024:.2f} MB")
                
                try:
                    shutil.rmtree(date_folder)
                    total_deleted += len(files)
                    total_size += folder_size
                    deleted_folders += 1
                except Exception as e:
                    logger.error(f"  [ERRO] Falha ao deletar {date_folder.name}: {e}")
        
        if deleted_folders == 0:
            logger.info(f"  [OK] Nenhuma gravacao antiga para deletar")
        
        cameras_processed += 1
    
    logger.info("="*60)
    logger.info(f"RESUMO: {cameras_processed} cameras processadas")
    logger.info(f"TOTAL: {total_deleted} arquivos deletados | {total_size/1024/1024:.2f} MB liberados")
    logger.info(f"PROTEGIDOS: {total_protected} clips mantidos")
    logger.info(f"Espaco liberado: {total_size/1024/1024/1024:.2f} GB")
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
