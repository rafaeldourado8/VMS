from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.core.cache import cache
from .services import DashboardService

class DashboardStatsAPIView(APIView):
    """
    Endpoint de alta performance para o Dashboard.
    Tenta ler do cache global antes de processar via Service.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 1. Tenta obter estatísticas globais do cache (populado via Celery Task)
        global_stats = cache.get("global_dashboard_stats")
        
        # 2. Se for um admin e quisermos os dados globais rápidos
        if request.user.is_staff and global_stats:
            return Response(global_stats)

        # 3. Fallback ou dados específicos do utilizador via Service
        stats_dto = DashboardService.get_user_stats(request.user)
        
        return Response({
            "total_cameras": stats_dto.total_cameras,
            "cameras_status": {
                "online": stats_dto.cameras_online,
                "offline": stats_dto.cameras_offline,
            },
            "detections_24h": stats_dto.total_detections_24h,
            "detections_by_type": stats_dto.detections_by_type,
            "recent_activity": stats_dto.recent_activity,
            "cached": False
        })