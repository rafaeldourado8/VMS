from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from .serializers import ConfiguracaoGlobalSerializer
from .services import ConfiguracaoGlobalService

class ConfiguracaoGlobalAPIView(APIView):
    """
    Endpoint administrativo para configurações globais.
    Utiliza o Serializer para coerção de tipos (ex: 'True' -> True).
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        dto = ConfiguracaoGlobalService.get_settings_dto()
        return Response(vars(dto))

    def patch(self, request):
        """Atualiza as definições garantindo a integridade dos tipos."""
        # 1. Validar e converter tipos via Serializer
        serializer = ConfiguracaoGlobalSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            # 2. Passar dados já convertidos (validated_data) para o serviço
            dto = ConfiguracaoGlobalService.update_settings(serializer.validated_data)
            return Response(vars(dto), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        return self.patch(request)