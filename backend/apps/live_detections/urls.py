from django.urls import path
from . import views

app_name = 'live_detections'

urlpatterns = [
    path('stats/', views.live_stats, name='stats'),
    path('camera/<int:camera_id>/stream/', views.camera_stream_info, name='stream_info'),
]
