from rest_framework.permissions import IsAdminUser  # Apenas Admins podem mudar!
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ConfiguracaoGlobal
from .serializers import ConfiguracaoGlobalSerializer


class ConfiguracaoGlobalAPIView(APIView):
    """
    Endpoint 8.1: Ler e Atualizar as Configurações Globais.

    - GET: Retorna o objeto de configurações.
    - PUT/PATCH: Atualiza o objeto de configurações.
    """

    # Apenas usuários com 'role=admin' (via IsAdminUser) podem mexer aqui.
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        """
        Retorna a configuração global única.
        """
        config = ConfiguracaoGlobal.load()  # Carrega o Singleton
        serializer = ConfiguracaoGlobalSerializer(config)
        return Response(serializer.data)

    def put(self, request, format=None):
        """
        Atualiza a configuração global única.
        """
        config = ConfiguracaoGlobal.load()

        # O 'partial=True' permite atualizações parciais (PATCH)
        serializer = ConfiguracaoGlobalSerializer(
            config, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    # Permite PATCH (sinônimo de PUT com partial=True)
    def patch(self, request, format=None):
        return self.put(request, format)
