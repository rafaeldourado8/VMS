"""
GT-Vision - Camera Views (Atualizado)
=====================================
Endpoints REST para gestão de câmeras.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import CameraSerializer
from .services import CameraService
from .schemas import CameraDTO


class CameraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para CRUD de câmeras.
    
    Endpoints:
    - GET    /api/cameras/           - Lista câmeras do usuário
    - POST   /api/cameras/           - Cria câmera + provisiona no MediaMTX
    - GET    /api/cameras/{id}/      - Detalhes de uma câmera
    - PUT    /api/cameras/{id}/      - Atualiza câmera
    - DELETE /api/cameras/{id}/      - Remove câmera + remove do MediaMTX
    - POST   /api/cameras/reprovision/ - Reprovisiona todas as câmeras no MediaMTX
    - GET    /api/cameras/{id}/stream_status/ - Status do stream
    """
    serializer_class = CameraSerializer
    permission_classes = [permissions.IsAuthenticated]
    service = CameraService()

    def get_queryset(self):
        """Retorna apenas câmeras do usuário autenticado."""
        return self.service.list_cameras_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Cria câmera e provisiona automaticamente no MediaMTX.
        
        Request Body:
        {
            "name": "Câmera Entrada",
            "stream_url": "rtsp://admin:pass@192.168.1.100:554/stream",
            "location": "Portaria Principal",
            "latitude": -23.5505,
            "longitude": -46.6333
        }
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro de validação: {serializer.errors}")
        serializer.is_valid(raise_exception=True)
        
        camera_dto = CameraDTO(
            owner_id=request.user.id,
            **serializer.validated_data
        )
        
        camera = self.service.create_camera(camera_dto)
        output_serializer = self.get_serializer(camera)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Remove câmera do banco e do MediaMTX."""
        instance = self.get_object()
        self.service.delete_camera(instance.id)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def reprovision(self, request):
        """
        Reprovisiona todas as câmeras do usuário no MediaMTX.
        
        Útil quando:
        - MediaMTX foi reiniciado
        - Câmeras não estão aparecendo no streaming
        - Sincronização de estado após manutenção
        
        Response:
        {
            "success": 5,
            "failed": 1,
            "total": 6,
            "message": "5/6 câmeras reprovisionadas com sucesso"
        }
        """
        results = self.service.reprovision_all_cameras(user=request.user)
        
        return Response({
            **results,
            "message": f"{results['success']}/{results['total']} câmeras reprovisionadas com sucesso"
        })

    @action(detail=True, methods=['get'])
    def stream_status(self, request, pk=None):
        """
        Retorna o status do stream de uma câmera específica.
        
        Response:
        {
            "status": "ready",
            "viewers": 3,
            "bytes_sent": 1234567,
            "hls_url": "/hls/cam_1/index.m3u8"
        }
        """
        camera = self.get_object()
        status_data = self.service.get_camera_stream_status(camera.id)
        return Response(status_data)

    @action(detail=True, methods=['post'])
    def update_detection_config(self, request, pk=None):
        """Atualiza configurações de detecção da câmera"""
        camera = self.get_object()
        config_data = request.data
        
        # Atualizar configurações de detecção
        if 'roi_areas' in config_data:
            camera.roi_areas = config_data['roi_areas']
        if 'virtual_lines' in config_data:
            camera.virtual_lines = config_data['virtual_lines']
        if 'tripwires' in config_data:
            camera.tripwires = config_data['tripwires']
        if 'zone_triggers' in config_data:
            camera.zone_triggers = config_data['zone_triggers']
        if 'recording_retention_days' in config_data:
            camera.recording_retention_days = config_data['recording_retention_days']
        
        camera.save()
        
        return Response({
            "success": True,
            "message": "Configurações de detecção atualizadas"
        })

    @action(detail=True, methods=['post'], url_path='toggle_ai')
    def toggle_ai(self, request, pk=None):
        """Alterna estado da IA para uma câmera"""
        camera = self.get_object()
        camera.ai_enabled = not getattr(camera, 'ai_enabled', False)
        camera.save()
        return Response({"success": True, "ai_enabled": camera.ai_enabled, "camera_id": camera.id})

    @action(detail=True, methods=['post'], url_path='start')
    def start_ai(self, request, pk=None):
        """Inicia IA para uma câmera (temporário até AI service estar pronto)"""
        camera = self.get_object()
        camera.ai_enabled = True
        camera.save()
        return Response({"success": True, "ai_enabled": True, "camera_id": camera.id})

    @action(detail=True, methods=['post'], url_path='stop')
    def stop_ai(self, request, pk=None):
        """Para IA para uma câmera (temporário até AI service estar pronto)"""
        camera = self.get_object()
        camera.ai_enabled = False
        camera.save()
        return Response({"success": True, "ai_enabled": False, "camera_id": camera.id})

    @action(detail=True, methods=['get'], url_path='status')
    def ai_status(self, request, pk=None):
        """Retorna status da IA para uma câmera (temporário até AI service estar pronto)"""
        camera = self.get_object()
        return Response({
            "camera_id": camera.id,
            "ai_enabled": getattr(camera, 'ai_enabled', False),
            "has_roi": bool(camera.roi_areas)
        })