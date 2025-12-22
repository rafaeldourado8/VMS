from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from apps.usuarios.views import LogoutAPIView, MeAPIView, MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

# Desabilita CSRF para o admin em ambiente de dev se necessário
admin.site.login = csrf_exempt(admin.site.login)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Endpoints de Autenticação Central
    path("api/auth/login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutAPIView.as_view(), name="token_blacklist"),
    path("api/auth/me/", MeAPIView.as_view(), name="auth_me"),

    # Inclusão dos Módulos Refatorados
    path("api/", include("apps.usuarios.urls")),
    path("api/", include("apps.cameras.urls")),
    path("api/", include("apps.deteccoes.urls")),
    path("api/", include("apps.dashboard.urls")),
    path("api/", include("apps.analytics.urls")),
    path("api/", include("apps.configuracoes.urls")),
    path("api/", include("apps.suporte.urls")),
    path("api/", include("apps.thumbnails.urls")),
]