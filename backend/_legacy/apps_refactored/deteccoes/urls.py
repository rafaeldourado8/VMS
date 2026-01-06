from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import DeteccaoViewSet, IngestDeteccaoAPIView

router = DefaultRouter()
router.register(r"detections", DeteccaoViewSet, basename="detection")

urlpatterns = [
    path("", include(router.urls)),
    # Endpoint manual para a ingestão rápida via API Key
    path("ingest/", IngestDeteccaoAPIView.as_view(), name="ingest-deteccao"),
]