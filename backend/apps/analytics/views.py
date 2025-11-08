# --- 1. Importar o sistema de cache do Django ---
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import AnalyticsService


class VehicleTypesAPIView(APIView):
    """
    Endpoint 5.3: Tipos de Veículos
    (Agora com cache de 5 minutos por usuário)
    """

    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 300  # 300 segundos = 5 minutos

    def get(self, request, format=None):
        user = request.user

        # --- 2. Definir a chave de cache ---
        cache_key = f"analytics_types_{user.id}"

        # --- 3. Tentar obter do cache ---
        data = cache.get(cache_key)

        # --- 4. Cache HIT ---
        if data:
            return Response({"data": data}, status=200)

        # --- 5. Cache MISS: Calcular os dados ---
        service = AnalyticsService(user=request.user)
        data = service.get_vehicle_type_distribution()

        # --- 6. Salvar no cache ---
        cache.set(cache_key, data, timeout=self.CACHE_TIMEOUT)

        return Response({"data": data}, status=200)


class DetectionsByPeriodAPIView(APIView):
    """
    Endpoint 5.2: Detecções por Período
    (Agora com cache de 5 minutos por usuário/período)
    """

    permission_classes = [IsAuthenticated]
    CACHE_TIMEOUT = 300  # 5 minutos

    def get(self, request, format=None):
        user = request.user
        period = request.query_params.get("period", "day")

        # --- 2. A chave de cache DEVE incluir o 'period' ---
        cache_key = f"analytics_period_{user.id}_{period}"

        # --- 3. Tentar obter do cache ---
        data = cache.get(cache_key)

        # --- 4. Cache HIT ---
        if data:
            return Response({"period": period, "data": data}, status=200)

        # --- 5. Cache MISS ---
        service = AnalyticsService(user=request.user)

        try:
            data = service.get_detections_by_period(period)

            # --- 6. Salvar no cache SÓ se for sucesso ---
            cache.set(cache_key, data, timeout=self.CACHE_TIMEOUT)

            return Response({"period": period, "data": data}, status=200)
        except ValueError as e:
            # Não fazemos cache de erros
            return Response({"error": str(e)}, status=400)
