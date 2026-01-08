from datetime import datetime, timedelta

from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..application.analytics.handlers import (

    GetDashboardHandler,
    GetMetricsHandler,
    GetAggregatedMetricsHandler
)
from ..application.analytics.queries import (
    GetDashboardQuery,
    GetMetricsQuery,
    GetAggregatedMetricsQuery
)
from ..infrastructure.analytics.django_metric_repository import DjangoMetricRepository
from ..domain.analytics.entities.metric import MetricType

class DashboardAPIView(APIView):
    """API para dados do dashboard."""
    
    def __init__(self):
        super().__init__()
        self._repository = DjangoMetricRepository()
        self._handler = GetDashboardHandler(self._repository)
    
    def get(self, request):
        """Retorna dados do dashboard."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = parse_datetime(start_date)
        if end_date:
            end_date = parse_datetime(end_date)
        
        query = GetDashboardQuery(start_date=start_date, end_date=end_date)
        result = self._handler.handle(query)
        
        return Response(result, status=status.HTTP_200_OK)

class MetricsAPIView(APIView):
    """API para métricas específicas."""
    
    def __init__(self):
        super().__init__()
        self._repository = DjangoMetricRepository()
        self._metrics_handler = GetMetricsHandler(self._repository)
        self._aggregated_handler = GetAggregatedMetricsHandler(self._repository)
    
    def get(self, request):
        """Retorna métricas por tipo."""
        metric_type = request.query_params.get('type', 'camera_status')
        start_date = parse_datetime(request.query_params.get('start_date', 
            (datetime.now() - timedelta(days=7)).isoformat()))
        end_date = parse_datetime(request.query_params.get('end_date', 
            datetime.now().isoformat()))
        aggregated = request.query_params.get('aggregated', 'false').lower() == 'true'
        
        try:
            metric_type_enum = MetricType(metric_type)
        except ValueError:
            return Response(
                {"error": "Tipo de métrica inválido"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if aggregated:
            aggregation = request.query_params.get('aggregation', 'avg')
            query = GetAggregatedMetricsQuery(
                metric_type=metric_type_enum,
                start_date=start_date,
                end_date=end_date,
                aggregation=aggregation
            )
            result = self._aggregated_handler.handle(query)
        else:
            query = GetMetricsQuery(
                metric_type=metric_type_enum,
                start_date=start_date,
                end_date=end_date
            )
            metrics = self._metrics_handler.handle(query)
            result = [
                {
                    "type": m.type.value,
                    "value": m.value,
                    "metadata": m.metadata,
                    "timestamp": m.timestamp
                }
                for m in metrics
            ]
        
        return Response(result, status=status.HTTP_200_OK)