from .views import DashboardAPIView, MetricsAPIView

from django.urls import path

urlpatterns = [
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path('metrics/', MetricsAPIView.as_view(), name='metrics'),
]