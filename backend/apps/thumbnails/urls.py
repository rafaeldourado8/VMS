from .views import CameraSnapshotView

from django.urls import path

urlpatterns = [
    path("thumbnails/<int:camera_id>/", CameraSnapshotView.as_view(), name="camera-snapshot"),
]