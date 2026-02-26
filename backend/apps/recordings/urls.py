from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecordingViewSet, verify_recording_access
from .views_secure import serve_recording

router = DefaultRouter()
router.register('recordings', RecordingViewSet)

urlpatterns = [
    path('serve/<int:camera_id>/<str:date>/<str:filename>/', serve_recording, name='serve-recording'),
    path('verify-access/', verify_recording_access, name='verify-recording-access'),
    path('', include(router.urls)),
]
