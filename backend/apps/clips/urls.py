from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ClipViewSet

router = DefaultRouter()
router.register(r'clips', ClipViewSet, basename='clips')

urlpatterns = router.urls