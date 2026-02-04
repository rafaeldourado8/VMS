from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_recording_snapshot(recording_id: int):
    """Task assíncrona para gerar snapshot de gravação."""
    from apps.cameras.services_snapshot import SnapshotCacheService
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    success = loop.run_until_complete(
        SnapshotCacheService.cache_recording_snapshot(recording_id)
    )
    
    return {"recording_id": recording_id, "success": success}

@shared_task
def process_recording_lpr(recording_id: int):
    """Task assíncrona para processar LPR de gravação."""
    from services.lpr.lpr_recording_processor import LPROfflineProcessor
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    processor = LPROfflineProcessor()
    loop.run_until_complete(processor.process_recording(recording_id))
    
    return {"recording_id": recording_id}
