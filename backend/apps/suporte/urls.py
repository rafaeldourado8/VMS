from .views import MensagemViewSet

from django.urls import include, path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# Registra a rota /api/support/chat/
router.register(r"support/chat", MensagemViewSet, basename="support-chat")

urlpatterns = [path("", include(router.urls))]
