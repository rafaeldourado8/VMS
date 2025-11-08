from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DeteccaoViewSet, IngestDeteccaoAPIView  # <--- Novo import

router = DefaultRouter()
router.register(r"detections", DeteccaoViewSet, basename="detection")

urlpatterns = [
    path("", include(router.urls)),
    # Rota para Ingestão de Detecções (POST /api/detections/ingest/)
    path("detections/ingest/", IngestDeteccaoAPIView.as_view(), name="ingest-deteccao"),
]
