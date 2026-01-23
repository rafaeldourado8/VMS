from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf.urls.static import static
from apps.usuarios.views import LogoutAPIView, MeAPIView, MyTokenObtainPairView, PlanInfoAPIView
from rest_framework_simplejwt.views import TokenRefreshView
from apps.cameras.views import CameraViewSet

# Customização do Django Admin
admin.site.site_header = "VMS Platform Admin"
admin.site.site_title = "VMS Admin"
admin.site.index_title = "Gerenciamento de Organizações e Planos"

# Desabilita CSRF para o admin em ambiente de dev se necessário
admin.site.login = csrf_exempt(admin.site.login)

urlpatterns = [
    path("admin/", admin.site.urls),
    
    # Health Check
    path("health/", include("apps.health.urls")),
    
    # Endpoints de Autenticação Central
    path("api/auth/login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutAPIView.as_view(), name="token_blacklist"),
    path("api/auth/me/", MeAPIView.as_view(), name="auth_me"),
    path("api/auth/plan/", PlanInfoAPIView.as_view(), name="plan_info"),

    # Inclusão dos Módulos Refatorados
    path("api/", include("apps.tenants.urls")),
    path("api/", include("apps.usuarios.urls")),
    path("api/", include("apps.cameras.urls")),
    path("api/", include("apps.deteccoes.urls")),
    path("api/", include("apps.clips.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    # path("api/", include("apps.analytics.urls")),  # TODO: Verificar implementação
    # path("api/", include("apps.configuracoes.urls")),  # TODO: Verificar implementação
    # path("api/", include("apps.suporte.urls")),  # TODO: Verificar implementação
    # path("api/", include("apps.thumbnails.urls")),  # TODO: Verificar implementação

    # Rotas temporárias de AI (até o serviço AI estar pronto)
    path("api/ai/cameras/<int:pk>/start/", CameraViewSet.as_view({'post': 'start_ai'}), name="ai_start"),
    path("api/ai/cameras/<int:pk>/stop/", CameraViewSet.as_view({'post': 'stop_ai'}), name="ai_stop"),
    path("api/ai/cameras/<int:pk>/status/", CameraViewSet.as_view({'get': 'ai_status'}), name="ai_status"),
]

# Servir arquivos de media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)