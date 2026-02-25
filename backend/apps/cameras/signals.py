"""
Signals para auto-provisionamento de câmeras
"""
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


class CamerasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cameras'

    def ready(self):
        """Executado quando o app está pronto."""
        import apps.cameras.signals  # noqa


@receiver(post_migrate)
def provision_cameras_on_startup(sender, **kwargs):
    """Provisiona todas as câmeras ativas após migrations."""
    if sender.name != 'apps.cameras':
        return
    
    # Desabilitado temporariamente para evitar erro de conexão durante migrations
    return
    
    import time
    import httpx
    
    streaming_url = 'http://streaming:8001'
    
    logger.info("⏳ Aguardando streaming service...")
    for i in range(10):
        try:
            resp = httpx.get(f"{streaming_url}/health", timeout=3.0)
            if resp.status_code == 200:
                break
        except:
            pass
        time.sleep(2)
    else:
        return
    
    try:
        from apps.cameras.models import Camera
        
        cameras = Camera.objects.filter(status='online')
        if cameras.count() == 0:
            return
        
        logger.info(f"🔄 Auto-provisionando {cameras.count()} câmeras...")
        
        success = 0
        with httpx.Client(timeout=30.0) as client:
            for camera in cameras:
                try:
                    resp = client.post(
                        f"{streaming_url}/cameras/provision",
                        json={
                            "camera_id": camera.id,
                            "rtsp_url": camera.stream_url,
                            "name": camera.name,
                            "enabled": True,
                            "on_demand": True
                        }
                    )
                    if resp.status_code == 200:
                        success += 1
                except:
                    pass
                time.sleep(1)
        
        logger.info(f"✅ {success}/{cameras.count()} câmeras OK")
        
    except Exception as e:
        logger.warning(f"⚠️ Erro: {e}")
