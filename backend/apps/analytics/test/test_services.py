import pytest

from django.utils import timezone

from apps.analytics.services import AnalyticsService
from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao

@pytest.mark.django_db
class TestAnalyticsService:
    def test_vehicle_distribution_calculation(self, admin_user):
        """Valida o cálculo de percentagens na distribuição de veículos."""
        cam = Camera.objects.create(owner=admin_user, name="C1", stream_url="rtsp://1")
        Deteccao.objects.create(camera=cam, timestamp=timezone.now(), vehicle_type="car")
        Deteccao.objects.create(camera=cam, timestamp=timezone.now(), vehicle_type="car")
        Deteccao.objects.create(camera=cam, timestamp=timezone.now(), vehicle_type="bus")

        service = AnalyticsService(admin_user)
        dist = service.get_vehicle_type_distribution()

        # 2 carros em 3 total = 66.7%
        car_stat = next(d for d in dist if d.type == "car")
        assert car_stat.count == 2
        assert car_stat.percentage == 66.7

    def test_detections_by_period_invalid_period(self, admin_user):
        """Garante que períodos inválidos levantam erro."""
        service = AnalyticsService(admin_user)
        with pytest.raises(ValueError):
            service.get_detections_by_period(period="invalid")