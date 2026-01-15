from .views import CameraViewSet, list_active_cameras_for_lpr

from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"cameras", CameraViewSet, basename="camera")

urlpatterns = [
    path("", include(router.urls)),
    path("cameras/lpr/active/", list_active_cameras_for_lpr, name="cameras-lpr-active"),
]