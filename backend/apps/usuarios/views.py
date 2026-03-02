# VMS/backend/apps/usuarios/views.py

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from rest_framework.decorators import action

from .serializers import UsuarioSerializer, MyTokenObtainPairSerializer
from .services import UsuarioService
from .schemas import UsuarioDTO
from .permissions import IsAdminOrReadOnly
from .security import LoginSecurityService, LoginRateThrottle

class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = UsuarioService.list_users()
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Uso de Dataclass conforme solicitado
        user_dto = UsuarioDTO(**serializer.validated_data)
        user = UsuarioService.create_user(user_dto)
        
        output_serializer = self.get_serializer(user)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    throttle_classes = [LoginRateThrottle]
    
    def post(self, request, *args, **kwargs):
        # Obter IP e email
        ip = LoginSecurityService.get_client_ip(request)
        email = request.data.get('email', '')
        identifier = f"{ip}:{email}"
        
        # Verificar lockout
        if LoginSecurityService.is_locked_out(identifier):
            return Response(
                {"detail": "Conta temporariamente bloqueada. Tente novamente em 5 minutos."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Tentar autenticar
        response = super().post(request, *args, **kwargs)
        
        # Se falhou
        if response.status_code != 200:
            locked, attempts = LoginSecurityService.record_failed_attempt(identifier)
            remaining = LoginSecurityService.MAX_ATTEMPTS - attempts
            
            if locked:
                return Response(
                    {"detail": "Muitas tentativas falhas. Conta bloqueada por 5 minutos."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            return Response(
                {"detail": f"Credenciais inválidas. {remaining} tentativas restantes."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Se sucesso, limpar tentativas
        LoginSecurityService.clear_failed_attempts(identifier)
        return response

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        try:
            token = RefreshToken(request.data["refresh_token"])
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except:
            return Response({"error": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST)