"""
VMS - Camera Views (DDD)
========================
Endpoints REST delegando para handlers da camada de aplicação.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import CameraSerializer
from .permissions import CameraAccessPermission
from infrastructure.persistence.django.repositories import DjangoCameraRepository
from application.monitoring.handlers import (
    CreateCameraHandler, DeleteCameraHandler, ListCamerasHandler,
    GetCameraHandler, GetCameraQuery, UpdateCameraHandler, UpdateCameraCommand
)
from application.monitoring.commands.create_camera_command import CreateCameraCommand
from application.monitoring.commands.delete_camera_command import DeleteCameraCommand
from application.monitoring.queries.list_cameras_query import ListCamerasQuery

class CameraViewSet(viewsets.ModelViewSet):
    serializer_class = CameraSerializer
    permission_classes = [permissions.IsAuthenticated, CameraAccessPermission]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        repo = DjangoCameraRepository()
        self.create_handler = CreateCameraHandler(repo)
        self.delete_handler = DeleteCameraHandler(repo)
        self.list_handler = ListCamerasHandler(repo)
        self.get_handler = GetCameraHandler(repo)
        self.update_handler = UpdateCameraHandler(repo)

    def get_queryset(self):
        query = ListCamerasQuery(owner_id=self.request.user.id)
        cameras = self.list_handler.handle(query)
        from apps.cameras.models import Camera
        return Camera.objects.filter(id__in=[c.id for c in cameras])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        command = CreateCameraCommand(
            owner_id=request.user.id,
            **serializer.validated_data
        )
        camera = self.create_handler.handle(command)
        
        from apps.cameras.models import Camera
        camera_model = Camera.objects.get(id=camera.id)
        output = self.get_serializer(camera_model)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        query = GetCameraQuery(camera_id=int(kwargs['pk']), owner_id=request.user.id)
        try:
            camera = self.get_handler.handle(query)
            from apps.cameras.models import Camera
            camera_model = Camera.objects.get(id=camera.id)
            serializer = self.get_serializer(camera_model)
            return Response(serializer.data)
        except ValueError:
            return Response({"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        
        command = UpdateCameraCommand(
            camera_id=int(kwargs['pk']),
            owner_id=request.user.id,
            **serializer.validated_data
        )
        try:
            camera = self.update_handler.handle(command)
            from apps.cameras.models import Camera
            camera_model = Camera.objects.get(id=camera.id)
            output = self.get_serializer(camera_model)
            return Response(output.data)
        except ValueError:
            return Response({"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        command = DeleteCameraCommand(camera_id=int(kwargs['pk']), owner_id=request.user.id)
        try:
            self.delete_handler.handle(command)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError:
            return Response({"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def reprovision(self, request):
        from .services import CameraService
        results = CameraService().reprovision_all_cameras(user=request.user)
        return Response({
            **results,
            "message": f"{results['success']}/{results['total']} câmeras reprovisionadas"
        })

    @action(detail=True, methods=['get'])
    def stream_status(self, request, pk=None):
        from .services import CameraService
        status_data = CameraService().get_camera_stream_status(int(pk))
        return Response(status_data)

    @action(detail=True, methods=['post'])
    def update_detection_config(self, request, pk=None):
        camera = self.get_object()
        for key in ['roi_areas', 'virtual_lines', 'tripwires', 'zone_triggers', 'recording_retention_days']:
            if key in request.data:
                setattr(camera, key, request.data[key])
        camera.save()
        return Response({"success": True, "message": "Configurações atualizadas"})

    @action(detail=True, methods=['post'], url_path='toggle_ai')
    def toggle_ai(self, request, pk=None):
        camera = self.get_object()
        camera.ai_enabled = not getattr(camera, 'ai_enabled', False)
        camera.save()
        return Response({"success": True, "ai_enabled": camera.ai_enabled, "camera_id": camera.id})

    @action(detail=True, methods=['post'], url_path='start')
    def start_ai(self, request, pk=None):
        camera = self.get_object()
        camera.ai_enabled = True
        camera.save()
        return Response({"success": True, "ai_enabled": True, "camera_id": camera.id})

    @action(detail=True, methods=['post'], url_path='stop')
    def stop_ai(self, request, pk=None):
        camera = self.get_object()
        camera.ai_enabled = False
        camera.save()
        return Response({"success": True, "ai_enabled": False, "camera_id": camera.id})

    @action(detail=True, methods=['get'], url_path='status')
    def ai_status(self, request, pk=None):
        camera = self.get_object()
        return Response({
            "camera_id": camera.id,
            "ai_enabled": getattr(camera, 'ai_enabled', False),
            "has_roi": bool(camera.roi_areas)
        })
