from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .serializers import DeteccaoSerializer, IngestDeteccaoSerializer
from .services import DeteccaoService
from .schemas import IngestDeteccaoDTO
from .permissions import HasIngestAPIKey

class DeteccaoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualização de detecções com suporte a filtros e cache."""
    serializer_class = DeteccaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Recupera os parâmetros de filtro da query string e consulta o serviço."""
        camera_id = self.request.query_params.get("camera_id")
        plate = self.request.query_params.get("plate")
        return DeteccaoService.list_for_user(self.request.user, camera_id, plate)

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        """Endpoint de listagem cacheado por 5 minutos."""
        return super().list(request, *args, **kwargs)

class IngestDeteccaoAPIView(APIView):
    """Endpoint de ingestão rápida para o Worker de IA."""
    permission_classes = [HasIngestAPIKey]
    authentication_classes = [] # Ingestão via API Key, sem necessidade de sessão/JWT

    def post(self, request):
        """Processa o recebimento de uma nova detecção."""
        serializer = IngestDeteccaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Mapeia para DTO e delega a criação ao serviço especializado
        dto = IngestDeteccaoDTO(**serializer.validated_data)
        deteccao = DeteccaoService.process_ingestion(dto)
        
        # Retorna o objeto formatado com o serializer de leitura
        response_data = DeteccaoSerializer(deteccao).data
        return Response(response_data, status=status.HTTP_201_CREATED)