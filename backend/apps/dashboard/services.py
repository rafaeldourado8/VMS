from .schemas import DashboardStatsDTO
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao

class DashboardService:
    """Serviço para consolidação de métricas e indicadores do dashboard."""

    @staticmethod
    def get_user_stats(user) -> DashboardStatsDTO:
        """Calcula estatísticas em tempo real para o utilizador autenticado."""
        now = timezone.now()
        last_24h = now - timedelta(hours=24)

        # 1. Métricas de Câmeras
        cameras = Camera.objects.filter(owner=user)
        total_cams = cameras.count()
        online_cams = cameras.filter(status="online").count()
        offline_cams = total_cams - online_cams

        # 2. Métricas de Detecções (Últimas 24h)
        detections_qs = Deteccao.objects.filter(
            camera__owner=user, 
            timestamp__gte=last_24h
        )
        total_det_24h = detections_qs.count()

        # 3. Agregação por Tipo de Veículo
        type_stats = (
            detections_qs.values("vehicle_type")
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        detections_by_type = {item["vehicle_type"]: item["total"] for item in type_stats}

        # 4. Atividade Recente (Últimas 5 detecções)
        recent = detections_qs.select_related("camera").order_by("-timestamp")[:5]
        recent_activity = [
            {
                "id": d.id,
                "camera": d.camera.name,
                "plate": d.plate,
                "time": d.timestamp,
                "type": d.vehicle_type
            }
            for d in recent
        ]

        return DashboardStatsDTO(
            total_cameras=total_cams,
            cameras_online=online_cams,
            cameras_offline=offline_cams,
            total_detections_24h=total_det_24h,
            detections_by_type=detections_by_type,
            recent_activity=recent_activity
        )