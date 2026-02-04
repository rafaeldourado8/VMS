from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CameraViewSet
from .ai_views import start_ai_processing, stop_ai_processing, get_ai_status
from .views_recordings import list_recordings, playback_recording

router = DefaultRouter()
router.register(r'cameras', CameraViewSet, basename='camera')

urlpatterns = [
    # Endpoints de gravações (antes do router para evitar conflitos)
    path('cameras/recordings/', list_recordings, name='recordings-list'),
    path('cameras/recordings/<int:camera_id>/', list_recordings, name='recordings-camera'),
    path('cameras/recordings/playback/<int:camera_id>/<str:date>/<str:filename>', playback_recording, name='recordings-playback'),
    
    # Endpoints dedicados ao controle da IA
    path('ai/cameras/<int:camera_id>/start/', start_ai_processing, name='ai-start'),
    path('ai/cameras/<int:camera_id>/stop/', stop_ai_processing, name='ai-stop'),
    path('ai/cameras/<int:camera_id>/status/', get_ai_status, name='ai-status'),
    
    # Router do ViewSet
    path('', include(router.urls)),
]