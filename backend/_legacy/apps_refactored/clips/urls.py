from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClipViewSet, MosaicoViewSet

router = DefaultRouter()
router.register(r'clips', ClipViewSet, basename='clips')
router.register(r'mosaicos', MosaicoViewSet, basename='mosaicos')

urlpatterns = [
    path('', include(router.urls)),
]