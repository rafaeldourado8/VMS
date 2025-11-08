# VMS/backend/apps/dashboard/views.py

# --- 1. Importar o sistema de cache do Django ---
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# Importamos os modelos de outros apps
from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao
from apps.deteccoes.serializers import DeteccaoSerializer


class StatsAPIView(APIView):
    """
    Endpoint 2.1: Estatísticas Gerais
    (Agora com cache de 60 segundos por usuário)
    """

    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 60  # Tempo do cache em segundos

    def get(self, request, format=None):
        user = request.user

        # --- 2. Definir uma chave de cache única para este usuário ---
        cache_key = f"dashboard_stats_{user.id}"

        # --- 3. Tentar obter os dados do cache ---
        data = cache.get(cache_key)

        # --- 4. Cache HIT: Se encontrarmos os dados, retornamos imediatamente ---
        if data:
            return Response(data, status=status.HTTP_200_OK)

        # --- 5. Cache MISS: Se não houver cache, calculamos os dados ---
        # (Esta é a lógica pesada que só corre se o cache falhar)
        all_cameras = Camera.objects.filter(owner=user)
        total_cameras = all_cameras.count()
        online_cameras = all_cameras.filter(status="online").count()
        offline_cameras = total_cameras - online_cameras

        total_detections_today = Deteccao.objects.filter(
            camera__owner=user, timestamp__date=timezone.now().date()
        ).count()

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
            "recent_events": [],
        }

        # --- 6. Salvar os dados recém-calculados no cache ---
        cache.set(cache_key, data, timeout=self.CACHE_TIMEOUT)

        return Response(data, status=status.HTTP_200_OK)


class RecentEventsAPIView(APIView):
    """
    Endpoint 2.2: Eventos Recentes
    (Agora com cache de 60 segundos por usuário)
    """

    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 60  # 60 segundos

    def get(self, request, format=None):
        user = request.user
        limit = int(request.query_params.get("limit", 10))

        # --- 1. A chave de cache deve incluir o 'limit' ---
        cache_key = f"dashboard_events_{user.id}_{limit}"

        # --- 2. Tentar obter do cache ---
        cached_data = cache.get(cache_key)

        # --- 3. Cache HIT ---
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # --- 4. Cache MISS ---
        events_queryset = Deteccao.objects.filter(camera__owner=user).order_by(
            "-timestamp"
        )[:limit]

        serializer = DeteccaoSerializer(events_queryset, many=True)
        # Importante: O formato da resposta é {"events": [...]}
        data = {"events": serializer.data}

        # --- 5. Salvar no cache ---
        cache.set(cache_key, data, timeout=self.CACHE_TIMEOUT)

        return Response(data, status=status.HTTP_200_OK)
