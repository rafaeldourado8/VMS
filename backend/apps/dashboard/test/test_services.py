from datetime import timedelta
import pytest

from django.utils import timezone

from apps.cameras.models import Camera
from apps.dashboard.services import DashboardService
from apps.deteccoes.models import Deteccao

@pytest.mark.django_db
class TestDashboardService:
    def test_get_user_stats_logic(self, admin_user):
        # Setup: 1 cam online, 1 detecção recente, 1 detecção antiga
        cam = Camera.objects.create(owner=admin_user, name="Cam", status="online", stream_url="rtsp://1")
        Deteccao.objects.create(camera=cam, timestamp=timezone.now(), vehicle_type="car")
        Deteccao.objects.create(camera=cam, timestamp=timezone.now() - timedelta(hours=48), vehicle_type="truck")

        stats = DashboardService.get_user_stats(admin_user)

        assert stats.total_cameras == 1
        assert stats.total_detections_24h == 1
        assert "car" in stats.detections_by_type
        assert "truck" not in stats.detections_by_type