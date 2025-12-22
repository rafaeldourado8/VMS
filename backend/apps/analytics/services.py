from django.db.models import Count
from django.db.models.functions import Trunc
from apps.deteccoes.models import Deteccao
from .schemas import VehicleDistributionDTO, DetectionPeriodDTO

class AnalyticsService:
    def __init__(self, user):
        self.user = user
        self.detections = Deteccao.objects.filter(camera__owner=self.user)

    def get_vehicle_type_distribution(self):
        total = self.detections.count()
        if total == 0:
            return []

        data_by_type = self.detections.values("vehicle_type").annotate(
            count=Count("vehicle_type")
        )

        return [
            VehicleDistributionDTO(
                type=item["vehicle_type"],
                count=item["count"],
                percentage=round((item["count"] / total) * 100, 1)
            )
            for item in data_by_type
        ]

    def get_detections_by_period(self, period="day"):
        period_map = {"hour": "hour", "day": "day", "week": "week", "month": "month"}
        trunc_kind = period_map.get(period)
        if not trunc_kind:
            raise ValueError("Período inválido")

        data = (
            self.detections.annotate(period_label=Trunc("timestamp", trunc_kind))
            .values("period_label")
            .annotate(count=Count("id"))
            .order_by("period_label")
        )

        return [
            DetectionPeriodDTO(date=item["period_label"].isoformat(), count=item["count"])
            for item in data
        ]