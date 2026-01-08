from django.urls import path
from .views import ClipAPIView

urlpatterns = [
    path('clips/', ClipAPIView.as_view(), name='clips'),
]