"""
Views para integração com streaming.
Mixin para adicionar funcionalidades de streaming a ViewSets existentes.
"""

import logging
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import StreamingService

logger = logging.getLogger(__name__)


class StreamingMixin:
    """
    Mixin para adicionar funcionalidades de streaming a ViewSets.
    
    Uso:
        class CameraViewSet(StreamingMixin, viewsets.ModelViewSet):
            queryset = Camera.objects.all()
            serializer_class = CameraSerializer
    """
    
    @action(detail=True, methods=['post'], url_path='start-stream')
    def start_stream(self, request, pk=None):
        """Inicia o stream de uma câmera."""
        camera = self.get_object()
        
        # Verificar se já tem stream
        if hasattr(camera, 'stream_id') and camera.stream_id:
            return Response(
                {
                    'detail': 'Stream já está ativo',
                    'stream_id': camera.stream_id,
                    'stream_url': StreamingService.get_stream_url_for_frontend(camera),
                    'websocket_url': StreamingService.get_websocket_url(camera)
                },
                status=status.HTTP_200_OK
            )
        
        # Criar stream
        stream_id = StreamingService.create_stream_for_camera(camera)
        
        if stream_id:
            return Response({
                'detail': 'Stream iniciado com sucesso',
                'stream_id': stream_id,
                'stream_url': StreamingService.get_stream_url_for_frontend(camera),
                'websocket_url': StreamingService.get_websocket_url(camera)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'detail': 'Falha ao iniciar stream'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='stop-stream')
    def stop_stream(self, request, pk=None):
        """Para o stream de uma câmera."""
        camera = self.get_object()
        
        success = StreamingService.delete_stream_for_camera(camera)
        
        if success:
            return Response(
                {'detail': 'Stream parado com sucesso'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'detail': 'Falha ao parar stream ou stream não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'], url_path='stream-status')
    def stream_status(self, request, pk=None):
        """Obtém o status do stream de uma câmera."""
        camera = self.get_object()
        
        stream_data = StreamingService.get_stream_status(camera)
        
        if stream_data:
            # Adicionar URLs para o frontend
            stream_data['stream_url'] = StreamingService.get_stream_url_for_frontend(camera)
            stream_data['websocket_url'] = StreamingService.get_websocket_url(camera)
            
            return Response(stream_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'detail': 'Stream não encontrado ou inativo'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], url_path='streaming-health')
    def streaming_health(self, request):
        """Verifica saúde do serviço de streaming."""
        is_healthy = StreamingService.health_check()
        
        return Response({
            'streaming_service': 'healthy' if is_healthy else 'unhealthy',
            'status': 'ok' if is_healthy else 'error'
        }, status=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE)