from typing import List

# (NOVO) Imports para cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Deteccao
from .permissions import HasIngestAPIKey

# 1. Importa AMBOS os serializers
from .serializers import DeteccaoSerializer, IngestDeteccaoSerializer


# Importante: Usamos ReadOnlyModelViewSet
class DeteccaoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint que permite às detecções serem vistas.
    (Seção 4.1 e 4.2 da documentação)

    Opcionalmente, permite filtrar por camera_id.
    Ex: /api/detections/?camera_id=1
    """

    serializer_class = DeteccaoSerializer
    permission_classes = [permissions.IsAuthenticated]  # Exige autenticação

    # (NOVO) Cacheia a resposta do endpoint LIST (GET /api/detections/)
    # por 5 minutos (300 segundos)
    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Esta view deve retornar uma lista de todas as detecções
        das câmeras que pertencem ao usuário autenticado.
        """
        user = self.request.user

        # 1. Filtra detecções APENAS das câmeras do usuário logado
        # (OTIMIZAÇÃO) Usa .select_related('camera') para buscar a câmera
        # associada na mesma query, evitando N+1 queries.
        queryset = Deteccao.objects.filter(camera__owner=user).select_related("camera")

        # 2. (Bônus) Permite filtrar por ID de câmera na URL
        camera_id = self.request.query_params.get("camera_id")
        if camera_id:
            queryset = queryset.filter(camera_id=camera_id)

        return queryset


class IngestDeteccaoAPIView(APIView):
    """
    Endpoint de Ingestão (POST): Recebe eventos de detecção do worker (Celery/FastAPI).
    Exige uma API Key interna (definida em settings.INGEST_API_KEY)
    enviada no header 'X-API-Key'.

    (Refatorado para usar IngestDeteccaoSerializer para validação)
    """

    permission_classes = [HasIngestAPIKey]
    authentication_classes: List = []

    def post(self, request, format=None):
        # 2. Usa o novo serializer de INGESTÃO para validar os dados
        #    que chegam no request.
        serializer = IngestDeteccaoSerializer(data=request.data)

        # 3. A mágica do DRF: O .is_valid() agora vai rodar
        #    automaticamente a nossa função 'validate_camera_id'
        #    e verificar se o timestamp é obrigatório.
        if serializer.is_valid():
            # 4. O .save() chama o método 'create' do nosso serializer,
            #    que sabe como criar a detecção com a instância da câmera.
            deteccao = serializer.save()

            # 5. IMPORTANTE: Para a *resposta*, usamos o serializer de LEITURA
            #    (DeteccaoSerializer) para formatar o JSON de saída
            #    corretamente (com 'camera_name', etc.).
            response_data = DeteccaoSerializer(deteccao).data

            return Response(response_data, status=status.HTTP_201_CREATED)

        # 6. Se a validação falhar (ex: Câmera não existe, timestamp faltando),
        #    o DRF retorna os erros formatados automaticamente.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
