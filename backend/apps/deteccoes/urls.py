"""
URLs da API de Deteccoes
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_lpr import LPRViewSet, ingest_lpr
from .views_webhook import webhook_push, webhook_test, webhook_hikvision

app_name = 'deteccoes'

router = DefaultRouter()
router.register(r'lpr', LPRViewSet, basename='lpr')

urlpatterns = [
    # Ingestao (usado pelo microsservico IA)
    path('ingest/', views.ingest_deteccao, name='ingest'),

    # Ingestao LPR (sem auth)
    path('lpr/ingest/', ingest_lpr, name='lpr_ingest'),

    # Webhook push (cameras Intelbras/Hikvision)
    path('webhook/push/', webhook_push, name='webhook_push'),
    path('webhook/push/<int:camera_id>/', webhook_push, name='webhook_push_camera'),
    path('webhook/hikvision/', webhook_hikvision, name='webhook_hikvision'),
    path('webhook/hikvision/<int:camera_id>/', webhook_hikvision, name='webhook_hikvision_camera'),
    path('webhook/test/', webhook_test, name='webhook_test'),

    # Listagem e consulta (usado pelo frontend)
    path('list/', views.list_deteccoes, name='list'),
    path('<int:pk>/', views.deteccao_detail, name='detail'),

    # LPR endpoints
    path('', include(router.urls)),
]
