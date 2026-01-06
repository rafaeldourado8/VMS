from celery import shared_task
from django.core.cache import cache
from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task(name="update_dashboard_stats")
def update_dashboard_stats_cache():
    """
    Calcula estatísticas pesadas globais e guarda no Redis com a estrutura 
    harmonizada com o DashboardStatsDTO.
    """
    try:
        total = Camera.objects.count()
        online = Camera.objects.filter(status='online').count()
        
        # Janela de 24h consistente com o serviço
        last_24h = timezone.now() - timedelta(hours=24)
        total_detections = Deteccao.objects.filter(timestamp__gte=last_24h).count()
        
        # Estrutura harmonizada (Câmaras aninhadas e chaves corretas)
        data = {
            "total_cameras": total,
            "cameras_status": {
                "online": online,
                "offline": total - online,
            },
            "detections_24h": total_detections,
            "detections_by_type": {}, 
            "recent_activity": [],
            "last_updated": timezone.now().isoformat(),
            "cached": True
        }
        
        cache.set("global_dashboard_stats", data, timeout=None)
        logger.info("Cache global do dashboard atualizado com sucesso.")
        
    except Exception as e:
        logger.error(f"Erro ao atualizar cache do dashboard: {e}")