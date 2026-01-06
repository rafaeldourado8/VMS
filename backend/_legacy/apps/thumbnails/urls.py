from django.urls import path
from .views import CameraSnapshotView

urlpatterns = [
    path("thumbnails/<int:camera_id>/", CameraSnapshotView.as_view(), name="camera-snapshot"),
]