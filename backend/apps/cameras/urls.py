from .views import CameraViewSet, internal_cameras_list

from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"cameras", CameraViewSet, basename="camera")

urlpatterns = [
    path("internal/cameras/", internal_cameras_list, name="internal_cameras"),
    path("", include(router.urls)),
]