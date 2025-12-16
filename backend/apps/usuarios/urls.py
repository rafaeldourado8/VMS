from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import UsuarioViewSet

# Cria o roteador para as rotas automáticas (CRUD de Usuários)
router = DefaultRouter()
router.register(r'users', UsuarioViewSet, basename='usuario')

urlpatterns = [
    # 1. Rotas de Autenticação (JWT) - O que faltava
    # POST /api/usuarios/token/ -> Retorna Access + Refresh Token (Login)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # POST /api/usuarios/token/refresh/ -> Renova o Access Token expirado
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 2. Rotas do ViewSet (CRUD)
    # Inclui /users/, /users/{id}/, etc.
    path('', include(router.urls)),
]