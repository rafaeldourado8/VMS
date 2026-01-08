import pytest

from django.core.cache import cache
from django.utils import timezone

from apps.cameras.models import Camera
from apps.dashboard.tasks import update_dashboard_stats_cache

@pytest.mark.django_db
def test_update_dashboard_stats_task(admin_user):
    """Verifica se a task popula o cache com a estrutura de objetos aninhados."""
    Camera.objects.create(owner=admin_user, name="Task Cam", status="online", stream_url="rtsp://task")
    
    update_dashboard_stats_cache()
    
    cached_data = cache.get("global_dashboard_stats")
    assert cached_data is not None
    assert "cameras_status" in cached_data
    assert cached_data["cameras_status"]["online"] == 1
    assert "detections_24h" in cached_data