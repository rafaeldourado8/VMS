from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import DeteccaoViewSet, IngestDeteccaoAPIView, FastIngestDeteccaoView

router = DefaultRouter()
router.register(r"detections", DeteccaoViewSet, basename="detection")

urlpatterns = [
    path("", include(router.urls)),
    
    # Endpoint para upload de arquivos (Multipart/Form-data) - Legado/Externo
    path("ingest/", IngestDeteccaoAPIView.as_view(), name="ingest-deteccao"),
    
    # NOVO: Endpoint para ingestão rápida via JSON + Base64 (Usado pelo AI Service)
    path("fast_ingest/", FastIngestDeteccaoView.as_view(), name="fast-ingest-deteccao"),
]