from rest_framework import viewsets, permissions
from .models import Camera
from .serializers import CameraSerializer

class CameraViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite às câmeras serem vistas ou editadas.
    (Seção 3 da documentação)
    """
    serializer_class = CameraSerializer
    permission_classes = [permissions.IsAuthenticated] # Exige autenticação

    def get_queryset(self):
        """
        Esta view deve retornar uma lista de todas as câmeras
        para o usuário autenticado atualmente.
        """
        user = self.request.user
        return Camera.objects.filter(owner=user).order_by('name')

    def perform_create(self, serializer):
        """
        Define automaticamente o 'owner' da nova câmera como o
        usuário que está fazendo o request.
        """
        serializer.save(owner=self.request.user)