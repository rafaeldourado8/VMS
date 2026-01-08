from .serializers import ConfiguracaoGlobalSerializer

from infrastructure.persistence.django.repositories.django_configuration_repository import DjangoConfigurationRepository
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from application.configuration import (

    GetConfigurationHandler, UpdateConfigurationHandler,
    GetConfigurationQuery, UpdateConfigurationCommand
)
from domain.configuration.exceptions import ConfigurationDomainException

class ConfiguracaoGlobalAPIView(APIView):
    """
    Endpoint administrativo para configurações globais usando DDD.
    """
    permission_classes = [IsAdminUser]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        repo = DjangoConfigurationRepository()
        self.get_handler = GetConfigurationHandler(repo)
        self.update_handler = UpdateConfigurationHandler(repo)

    def get(self, request):
        try:
            query = GetConfigurationQuery()
            config = self.get_handler.handle(query)
            
            return Response({
                "notifications_enabled": config.notifications_enabled,
                "support_email": config.support_email.value,
                "maintenance_mode": config.maintenance_mode,
                "system_available": config.is_system_available()
            })
        except ConfigurationDomainException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        """Atualiza as configurações usando DDD"""
        serializer = ConfiguracaoGlobalSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Mapear campos do serializer para o command
            command_data = {}
            if 'notificacoes_habilitadas' in serializer.validated_data:
                command_data['notifications_enabled'] = serializer.validated_data['notificacoes_habilitadas']
            if 'email_suporte' in serializer.validated_data:
                command_data['support_email'] = serializer.validated_data['email_suporte']
            if 'em_manutencao' in serializer.validated_data:
                command_data['maintenance_mode'] = serializer.validated_data['em_manutencao']
            
            command = UpdateConfigurationCommand(**command_data)
            config = self.update_handler.handle(command)
            
            return Response({
                "notifications_enabled": config.notifications_enabled,
                "support_email": config.support_email.value,
                "maintenance_mode": config.maintenance_mode,
                "system_available": config.is_system_available()
            }, status=status.HTTP_200_OK)
            
        except ConfigurationDomainException as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)