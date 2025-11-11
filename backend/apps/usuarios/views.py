from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

# --- 1. Importe as novas classes ---
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, UsuarioSerializer

from .models import Usuario
from .permissions import IsAdminOrReadOnly


# --- Esta é a view /api/auth/me/ ---
class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- 2. Adicione esta nova View de Login ---
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Usa o nosso serializer customizado para o login.
    """
    serializer_class = MyTokenObtainPairSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Usuario.objects.all().order_by("-created_at")
    serializer_class = UsuarioSerializer


class LogoutAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(
                {"error": "Token inválido ou ausente."},
                status=status.HTTP_400_BAD_REQUEST,
            )