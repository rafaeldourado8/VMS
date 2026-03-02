from django.urls import path
from .views import NotificationPreferenceViewSet, NotificationLogViewSet, LoginLogViewSet

app_name = 'notifications'

urlpatterns = [
    # Login Logs (Admin only)
    path('login-logs/', LoginLogViewSet.as_view({
        'get': 'list',
    }), name='login-logs-list'),
    
    path('login-logs/<int:pk>/', LoginLogViewSet.as_view({
        'get': 'retrieve',
    }), name='login-logs-detail'),
    
    # Preferências
    path('preferences/', NotificationPreferenceViewSet.as_view({
        'get': 'list',
        'put': 'update',
        'patch': 'update',
    }), name='preferences'),
    
    # Logs
    path('logs/', NotificationLogViewSet.as_view({
        'get': 'list',
    }), name='logs-list'),
    
    path('logs/<int:pk>/', NotificationLogViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy',
    }), name='logs-detail'),
    
    path('logs/<int:pk>/mark-as-read/', NotificationLogViewSet.as_view({
        'post': 'mark_as_read',
    }), name='logs-mark-as-read'),
    
    path('logs/mark-all-as-read/', NotificationLogViewSet.as_view({
        'post': 'mark_all_as_read',
    }), name='logs-mark-all-as-read'),
    
    path('logs/delete-all/', NotificationLogViewSet.as_view({
        'delete': 'delete_all',
    }), name='logs-delete-all'),
]
