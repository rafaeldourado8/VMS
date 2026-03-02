from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from .models import NotificationPreference, NotificationLog, LoginLog
from .serializers import NotificationPreferenceSerializer, NotificationLogSerializer, LoginLogSerializer
from .services import NotificationService


class LoginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para logs de login (apenas admin)"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = LoginLogSerializer
    queryset = LoginLog.objects.all()
    
    def get_queryset(self):
        """Filtra por usuário se fornecido"""
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset


class NotificationPreferenceViewSet(viewsets.ViewSet):
    """ViewSet para preferências de notificação"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Retorna preferências do usuário atual"""
        prefs = NotificationService.get_or_create_preferences(request.user)
        serializer = NotificationPreferenceSerializer(prefs)
        return Response(serializer.data)
    
    def update(self, request):
        """Atualiza preferências do usuário"""
        prefs = NotificationService.get_or_create_preferences(request.user)
        serializer = NotificationPreferenceSerializer(prefs, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationLogViewSet(viewsets.ModelViewSet):
    """ViewSet para logs de notificações"""
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationLogSerializer
    http_method_names = ['get', 'delete', 'post']
    
    def get_queryset(self):
        """Retorna apenas notificações do usuário atual"""
        return NotificationLog.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marca notificação como lida"""
        from django.utils import timezone
        
        notification = self.get_object()
        notification.read_at = timezone.now()
        notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marca todas as notificações como lidas"""
        from django.utils import timezone
        
        count = NotificationLog.objects.filter(
            user=request.user,
            read_at__isnull=True
        ).update(read_at=timezone.now())
        
        return Response({'marked': count})
    
    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        """Apaga todas as notificações do usuário"""
        count = NotificationLog.objects.filter(user=request.user).count()
        NotificationLog.objects.filter(user=request.user).delete()
        
        return Response({'deleted': count})
