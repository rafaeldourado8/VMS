from .views import CameraViewSet

from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"cameras", CameraViewSet, basename="camera")

urlpatterns = [path("", include(router.urls))]