from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CameraViewSet, cameras_for_recorder, list_recordings
from .views_recordings import playback_recording
from .ai_views import start_ai_processing, stop_ai_processing, get_ai_status

router = DefaultRouter()
router.register(r'cameras', CameraViewSet, basename='camera')

urlpatterns = [
    path('cameras/recorder/', cameras_for_recorder, name='cameras-recorder'),
    path('cameras/recordings/', list_recordings, name='recordings-list'),
    path('cameras/recordings/playback/<int:camera_id>/<str:date>/<str:filename>', playback_recording, name='recording-playback'),
    path('ai/cameras/<int:camera_id>/start/', start_ai_processing, name='ai-start'),
    path('ai/cameras/<int:camera_id>/stop/', stop_ai_processing, name='ai-stop'),
    path('ai/cameras/<int:camera_id>/status/', get_ai_status, name='ai-status'),
    path('', include(router.urls)),
]