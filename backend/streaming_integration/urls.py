"""
URLs para integração com streaming.
"""

from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import StreamingService

@api_view(['GET'])
def streaming_health_check(request):
    """Endpoint de health check do serviço de streaming."""
    is_healthy = StreamingService.health_check()
    return Response({
        'streaming_service': 'healthy' if is_healthy else 'unhealthy'
    })

urlpatterns = [
    path('streaming/health/', streaming_health_check, name='streaming-health'),
]