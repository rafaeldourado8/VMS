from celery import shared_task
from django.core.cache import cache
from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task(name="update_dashboard_stats")
def update_dashboard_stats_cache():
    """
    Calcula estatísticas pesadas e salva no Redis.
    Executar via Celery Beat a cada 10 ou 30 segundos.
    """
    try:
        total = Camera.objects.count()
        # Nota: 'status' online/offline pode requerer checagem real no futuro,
        # aqui usamos o valor do banco para performance.
        online = Camera.objects.filter(status='online').count()
        
        # Contagem de detecções do dia (pode ser pesada com 5k câmeras)
        today = timezone.now().date()
        total_detections = Deteccao.objects.filter(timestamp__date=today).count()
        
        data = {
            "total_cameras": total,
            "online_cameras": online,
            "offline_cameras": total - online,
            "total_detections_today": total_detections,
            # Adicione metadados de timestamp para o frontend saber quão fresco é
            "last_updated": timezone.now().isoformat()
        }
        
        # Salva no Redis com chave global
        cache.set("global_dashboard_stats", data, timeout=None)
        logger.info("Cache do dashboard atualizado com sucesso.")
        
    except Exception as e:
        logger.error(f"Erro ao atualizar cache do dashboard: {e}")