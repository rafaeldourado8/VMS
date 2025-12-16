"""
URL configuration for config project.
"""

# 1. Importe as suas views customizadas
from apps.usuarios.views import LogoutAPIView, MeAPIView, MyTokenObtainPairView
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
# 2. Remova 'TokenObtainPairView' e importe apenas 'TokenRefreshView'
from rest_framework_simplejwt.views import TokenRefreshView

# Desabilita CSRF para admin em desenvolvimento
admin.site.login = csrf_exempt(admin.site.login)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Autenticação JWT
    # 3. Use a sua 'MyTokenObtainPairView' customizada para o login
    path("api/auth/login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutAPIView.as_view(), name="token_blacklist"),
    
    # Rota /api/auth/me/ (para o PrivateRoute.tsx)
    path("api/auth/me/", MeAPIView.as_view(), name="auth_me"),

    # Nossos apps
    path("api/", include("apps.usuarios.urls")),
    path("api/", include("apps.cameras.urls")),
    path("api/", include("apps.deteccoes.urls")),
    path("api/", include("apps.dashboard.urls")),
    path("api/", include("apps.analytics.urls")),
    path("api/", include("apps.configuracoes.urls")),
    path("api/", include("apps.suporte.urls")),
    path('api/', include('streaming_integration.urls')),
    path("api/", include("apps.thumbnails.urls")),
]