from .views import ConfiguracaoGlobalAPIView

from django.urls import path

urlpatterns = [
    # Endpoint 8.1: /api/settings/
    path("settings/", ConfiguracaoGlobalAPIView.as_view(), name="global-settings")
]
