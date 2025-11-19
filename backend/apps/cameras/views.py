from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .serializers import CameraSerializer
from .services import CameraService  

class CameraViewSet(viewsets.ModelViewSet):
    """
    API endpoint para câmeras.
    Refatorado para ser uma 'Thin View', delegando lógica para o CameraService.
    """
    serializer_class = CameraSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Numa aplicação maior, isto seria injetado via Dependency Injection
    service = CameraService()

    def get_queryset(self):
        """
        Delega a consulta ao serviço.
        """
        return self.service.list_cameras_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Sobrescreve o create para usar o serviço em vez do comportamento padrão.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # O serviço trata da criação e associação do owner
        camera = self.service.create_camera(
            user=request.user, 
            data=serializer.validated_data
        )
        
        # Serializa o objeto criado para retornar ao frontend
        output_serializer = self.get_serializer(camera)
        headers = self.get_success_headers(output_serializer.data)
        
        return Response(
            output_serializer.data, 
            status=status.HTTP_201_CREATED, 
            headers=headers
        )
