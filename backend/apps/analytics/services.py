from django.db.models import Count
from django.db.models.functions import Trunc

from apps.deteccoes.models import Deteccao


class AnalyticsService:
    """
    Abstrai as consultas complexas de analytics para um usuário específico.
    """

    def __init__(self, user):
        self.user = user
        # Queryset base: Apenas detecções do usuário logado
        self.detections = Deteccao.objects.filter(camera__owner=self.user)

    def get_vehicle_type_distribution(self):
        """
        Calcula a contagem e porcentagem de cada tipo de veículo.
        (Lógica da antiga VehicleTypesAPIView)
        """
        total_detections = self.detections.count()
        if total_detections == 0:
            return []

        data_by_type = self.detections.values("vehicle_type").annotate(
            count=Count("vehicle_type")
        )

        response_data = []
        for item in data_by_type:
            count = item["count"]
            percentage = (count / total_detections) * 100
            response_data.append(
                {
                    "type": item["vehicle_type"],
                    "count": count,
                    "percentage": round(percentage, 1),
                }
            )
        return response_data

    def get_detections_by_period(self, period="day"):
        """
        Agrupa detecções por 'hour', 'day', 'week' ou 'month'.
        (Lógica da antiga DetectionsByPeriodAPIView)
        """
        period_map = {"hour": "hour", "day": "day", "week": "week", "month": "month"}

        # Valida o período
        trunc_kind = period_map.get(period)
        if not trunc_kind:
            # Você pode levantar uma exceção customizada aqui
            raise ValueError("Período inválido")

        data = (
            self.detections.annotate(period_label=Trunc("timestamp", trunc_kind))
            .values("period_label")
            .annotate(count=Count("id"))
            .order_by("period_label")
        )

        return [
            {"date": item["period_label"].isoformat(), "count": item["count"]}
            for item in data
        ]
