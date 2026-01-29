"""
URLs da API de Detecções
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views_lpr import LPRViewSet, ingest_lpr

app_name = 'deteccoes'

router = DefaultRouter()
router.register(r'lpr', LPRViewSet, basename='lpr')

urlpatterns = [
    # Ingestão (usado pelo microsserviço IA)
    path('ingest/', views.ingest_deteccao, name='ingest'),
    
    # Ingestão LPR (sem auth)
    path('lpr/ingest/', ingest_lpr, name='lpr_ingest'),
    
    # Listagem e consulta (usado pelo frontend)
    path('list/', views.list_deteccoes, name='list'),
    path('<int:pk>/', views.deteccao_detail, name='detail'),
    
    # LPR endpoints
    path('', include(router.urls)),
]
