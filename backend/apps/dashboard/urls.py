from django.urls import path
from .views import DashboardStatsAPIView, dashboard_stream

urlpatterns = [
    path("stats/", DashboardStatsAPIView.as_view(), name="dashboard-stats"),
    path("stream/", dashboard_stream, name="dashboard-stream"),
]