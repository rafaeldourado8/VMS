from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CameraViewSet

router = DefaultRouter()
# Registra a rota /cameras/
router.register(r"cameras", CameraViewSet, basename="camera")

urlpatterns = [path("", include(router.urls))]
