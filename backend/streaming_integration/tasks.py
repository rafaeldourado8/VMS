from celery import shared_task
from .client import mediamtx_api_client
import logging

logger = logging.getLogger(__name__)

@shared_task(name="sync_camera_mediamtx", bind=True, max_retries=3, default_retry_delay=5)
def sync_camera_mediamtx(self, camera_id: str, rtsp_url: str):
    """
    Tarefa assíncrona para configurar a câmera no MediaMTX.
    """
    try:
        logger.info(f"[Async] Configurando câmera {camera_id} no MediaMTX... ({rtsp_url})")
        success = mediamtx_api_client.add_or_update_camera(camera_id, rtsp_url)
        if not success:
            raise Exception("Falha na resposta da API MediaMTX")
    except Exception as exc:
        logger.exception(f"[Async] Erro ao sincronizar câmera {camera_id}: {exc}")
        raise self.retry(exc=exc)

@shared_task(name="remove_camera_mediamtx")
def remove_camera_mediamtx(camera_id: str):
    """
    Tarefa assíncrona para remover câmera.
    """
    logger.info(f"[Async] Removendo câmera {camera_id} do MediaMTX...")
    mediamtx_api_client.remove_camera(camera_id)