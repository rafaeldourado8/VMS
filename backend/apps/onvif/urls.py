from django.urls import path
from . import views

urlpatterns = [
    path('cameras/<int:camera_id>/recordings/<str:date>/', views.list_recordings, name='onvif-recordings'),
    path('playback/<int:camera_id>/<str:date>/<str:time>.m3u8', views.playback_manifest, name='onvif-manifest'),
    path('playback/<int:camera_id>/<str:date>/<str:time>_<str:segment>', views.playback_segment, name='onvif-segment'),
]
