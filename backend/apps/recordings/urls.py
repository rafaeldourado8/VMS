from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecordingViewSet, verify_recording_access

router = DefaultRouter()
router.register('recordings', RecordingViewSet)

urlpatterns = [
    path('verify-access/', verify_recording_access, name='verify-recording-access'),
    path('', include(router.urls)),
]
