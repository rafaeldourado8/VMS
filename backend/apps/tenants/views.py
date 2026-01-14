from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Organization, Subscription
from .serializers import OrganizationSerializer, SubscriptionSerializer
from .permissions import IsPlatformAdmin, IsOrganizationMember

class OrganizationViewSet(viewsets.ModelViewSet):
    """Apenas Platform Admins podem gerenciar organizações"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsPlatformAdmin]

class SubscriptionViewSet(viewsets.ModelViewSet):
    """Apenas Platform Admins podem gerenciar planos"""
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsPlatformAdmin]
    
    @action(detail=False, methods=['get'])
    def my_subscription(self, request):
        """Retorna subscription da organização do usuário"""
        if not request.user.organization:
            return Response({'error': 'Usuário sem organização'}, status=status.HTTP_404_NOT_FOUND)
        
        subscription = getattr(request.user.organization, 'subscription', None)
        if not subscription:
            return Response({'error': 'Organização sem plano'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(subscription)
        return Response(serializer.data)
