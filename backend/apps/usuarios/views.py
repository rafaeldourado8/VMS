from rest_framework import viewsets, permissions
from .models import Usuario
from .serializers import UsuarioSerializer
from .permissions import IsAdminOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

class UsuarioViewSet(viewsets.ModelViewSet):

    permission_classes = [IsAdminOrReadOnly] # Permissão corrigida (Admin para escrita, Autenticado para leitura)
    """
    API endpoint que permite aos usuários serem vistos ou editados.
    (Endpoints 7.1, 7.2, 7.3, 7.4)
    """
    queryset = Usuario.objects.all().order_by('-created_at')
    serializer_class = UsuarioSerializer

    # A linha 'permission_classes = [permissions.IsAuthenticated]' duplicada foi removida.

class LogoutAPIView(APIView):
    """
    Endpoint 1.2: Logout
    Usa AllowAny para evitar a verificação do Access Token na Header,
    focando apenas em colocar o Refresh Token na lista negra.
    """
    # Apenas exigimos que o token (que está no Body) seja um token válido.
    permission_classes = [permissions.AllowAny] # <--- Mudamos para AllowAny

    def post(self, request):
        try:
            # Pega o refresh token enviado no corpo da requisição
            refresh_token = request.data["refresh_token"] 
            token = RefreshToken(refresh_token)
            token.blacklist() # Coloca o token na lista negra
            
            # Retorna 205 Reset Content (o padrão para logout bem-sucedido)
            return Response(status=status.HTTP_205_RESET_CONTENT)
        
        except Exception as e:
            # Se o token estiver faltando ou for inválido
            return Response({"error": "Token inválido ou ausente."}, status=status.HTTP_400_BAD_REQUEST)