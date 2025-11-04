from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MensagemViewSet

router = DefaultRouter()
# Registra a rota /api/support/chat/
router.register(r'support/chat', MensagemViewSet, basename='support-chat')

urlpatterns = [
    path('', include(router.urls)),
]