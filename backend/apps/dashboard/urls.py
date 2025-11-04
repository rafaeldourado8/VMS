from django.urls import path
from .views import StatsAPIView, RecentEventsAPIView # <--- Novo import

urlpatterns = [
    # Endpoint 2.1
    path('dashboard/stats/', StatsAPIView.as_view(), name='dashboard-stats'),

    # Endpoint 2.2 (NOVO)
    path('dashboard/recent-events/', RecentEventsAPIView.as_view(), name='dashboard-recent-events'), 
]