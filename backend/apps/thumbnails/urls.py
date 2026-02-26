from django.urls import path
from .views import CameraSnapshotView, clear_thumbnail_cache

urlpatterns = [
    path("thumbnails/<int:camera_id>/", CameraSnapshotView.as_view(), name="camera-snapshot"),
    path("thumbnails/clear/", clear_thumbnail_cache, name="clear-all-cache"),
    path("thumbnails/<int:camera_id>/clear/", clear_thumbnail_cache, name="clear-camera-cache"),
]