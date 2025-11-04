from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from apps.deteccoes.serializers import DeteccaoSerializer

# Importamos os modelos de outros apps
from apps.cameras.models import Camera 
from apps.deteccoes.models import Deteccao 

class StatsAPIView(APIView):
    """
    Endpoint 2.1: Estatísticas Gerais
    Retorna o status geral do sistema do ponto de vista do usuário.
    """
    permission_classes = [IsAuthenticated] # Exige autenticação

    def get(self, request, format=None):
        user = request.user

        # 1. Total de Câmeras do Usuário
        all_cameras = Camera.objects.filter(owner=user)
        total_cameras = all_cameras.count()

        # 2. Status Online/Offline
        online_cameras = all_cameras.filter(status='online').count()
        offline_cameras = total_cameras - online_cameras

        # 3. Total de Detecções (do Usuário)
        # Filtramos as detecções que pertencem às câmeras DESTE usuário
        total_detections_today = Deteccao.objects.filter(
            camera__owner=user, 
            timestamp__date=timezone.now().date()
        ).count()

        # Nota: O uso de CPU/Memória/GPU geralmente é lido de outro serviço (Docker/Servidor)
        # Aqui, vamos mockar (simular) esses valores.

        data = {
            # Estatísticas do Servidor (Simuladas)
            "cpu_usage": 0,
            "gpu_usage": None,
            "memory_usage": 0.0,
            "memory_total": 16.0,

            # Estatísticas do Projeto (Reais)
            "total_cameras": total_cameras,
            "online_cameras": online_cameras,
            "offline_cameras": offline_cameras,
            "total_detections_today": total_detections_today,
            "recent_events": [], # Vamos preencher isso no próximo endpoint
        }

        return Response(data, status=status.HTTP_200_OK)
    
class RecentEventsAPIView(APIView):
    """
    Endpoint 2.2: Eventos Recentes
    Retorna as últimas detecções limitadas para o dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        limit = int(request.query_params.get('limit', 10)) # Pega o limite da query (padrão: 10)

        # 1. Filtra detecções APENAS das câmeras do usuário logado
        # 2. Ordena por timestamp (mais recente) e limita pelo parâmetro 'limit'
        events_queryset = Deteccao.objects.filter(
            camera__owner=user
        ).order_by('-timestamp')[:limit]

        # Serializa os dados (os traduz para JSON)
        serializer = DeteccaoSerializer(events_queryset, many=True)

        # Retorna o JSON no formato da sua documentação
        return Response({"events": serializer.data}, status=status.HTTP_200_OK)