import pytest
import json
from apps.deteccoes.tasks import process_detection_message

@pytest.mark.django_db
def test_celery_task_processing(admin_user):
    """Testa se a task do Celery consegue processar um JSON bruto."""
    from apps.cameras.models import Camera
    camera = Camera.objects.create(owner=admin_user, name="Task Cam", stream_url="rtsp://task")
    
    message = json.dumps({
        "camera_id": camera.id,
        "timestamp": "2025-10-16T14:59:47Z",
        "plate": "CEL1234",
        "vehicle_type": "bus"
    })
    
    # Chama a função diretamente para teste
    process_detection_message(message)
    
    from apps.deteccoes.models import Deteccao
    assert Deteccao.objects.filter(plate="CEL1234").exists()