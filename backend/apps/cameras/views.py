from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .serializers import CameraSerializer
from .services import CameraService  
from .schemas import CameraDTO

class CameraViewSet(viewsets.ModelViewSet):
    """Thin View: Delega lógica para o CameraService."""
    serializer_class = CameraSerializer
    permission_classes = [permissions.IsAuthenticated]
    service = CameraService()

    def get_queryset(self):
        return self.service.list_cameras_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        camera_dto = CameraDTO(
            owner_id=request.user.id,
            **serializer.validated_data
        )
        
        camera = self.service.create_camera(camera_dto)
        output_serializer = self.get_serializer(camera)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.service.delete_camera(instance.id)
        return Response(status=status.HTTP_204_NO_CONTENT)