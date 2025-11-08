from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UsuarioViewSet

# Cria um roteador
router = DefaultRouter()

# Registra nossa ViewSet com o roteador
# O DRF vai criar as URLs: /users/, /users/{id}/, etc.
router.register(r"users", UsuarioViewSet, basename="usuario")

# As URLs da API são agora determinadas automaticamente pelo roteador
urlpatterns = [path("", include(router.urls))]
