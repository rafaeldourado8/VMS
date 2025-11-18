"""
URLs para integração com streaming. (OBSOLETO PÓS-MEDIAMTX)
"""

from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
# from .services import StreamingService # Obsoleto

# O endpoint 'streaming_health_check' foi removido pois
# o 'streaming_service' não existe mais.

urlpatterns = [
    # path('streaming/health/', streaming_health_check, name='streaming-health'),
]