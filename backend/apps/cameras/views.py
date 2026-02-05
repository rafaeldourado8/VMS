"""
GT-Vision - Camera Views (Atualizado)
=====================================
Endpoints REST para gestão de câmeras.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import Camera
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
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    permission_classes = [permissions.IsAuthenticated]
    service = CameraService()

    def get_queryset(self):
        """Retorna apenas câmeras do usuário autenticado."""
        return self.service.list_cameras_for_user(self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Cria câmera e provisiona automaticamente no MediaMTX.
        Nome será: username_gtvision_nome_fornecido
        
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
        serializer.is_valid(raise_exception=True)
        
        # Usar nome original sem prefixo
        original_name = serializer.validated_data['name']
        
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
        if 'onvif_host' in config_data:
            camera.onvif_host = config_data['onvif_host']
        if 'onvif_port' in config_data:
            camera.onvif_port = config_data['onvif_port']
        if 'onvif_username' in config_data:
            camera.onvif_username = config_data['onvif_username']
        if 'onvif_password' in config_data:
            camera.onvif_password = config_data['onvif_password']
        
        camera.save()
        
        return Response({
            "success": True,
            "message": "Configurações atualizadas"
        })

    @action(detail=True, methods=['post'])
    def start_ai(self, request, pk=None):
        """Inicia detecção de IA para a câmera"""
        camera = self.get_object()
        success = self.service._start_ai_processing(camera)
        
        if success:
            return Response({"success": True, "message": "IA iniciada"})
        return Response({"success": False, "message": "Falha ao iniciar IA"}, status=500)

    @action(detail=False, methods=['post'])
    def start_all_ai(self, request):
        """Inicia IA para todas as câmeras do usuário"""
        cameras = self.get_queryset()
        results = {"success": 0, "failed": 0, "total": cameras.count()}
        
        for camera in cameras:
            if self.service._start_ai_processing(camera):
                results["success"] += 1
            else:
                results["failed"] += 1
        
        return Response({
            **results,
            "message": f"{results['success']}/{results['total']} câmeras com IA iniciada"
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def cameras_for_recorder(request):
    """Endpoint público para o recorder buscar câmeras."""
    try:
        cameras = Camera.objects.filter(status='online').values(
            'id', 'name', 'stream_url', 'status'
        )
        return Response(list(cameras))
    except Exception as e:
        return Response(
            {"error": str(e), "cameras": []},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_recordings(request):
    """
    Lista gravações disponíveis por câmera e período.
    
    Query params:
    - camera_id: ID da câmera (obrigatório)
    - date: Data no formato YYYY-MM-DD (obrigatório)
    - start_time: Hora inicial HH:MM (opcional)
    - end_time: Hora final HH:MM (opcional)
    
    Response:
    {
        "camera_id": 1,
        "date": "2025-01-20",
        "recordings": [
            {
                "filename": "14-30-00.mp4",
                "start_time": "14:30:00",
                "size_mb": 125.5,
                "duration_seconds": 3600,
                "playback_url": "/playback/cam_1/2025-01-20/14-30-00.mp4/index.m3u8"
            }
        ],
        "total_size_mb": 500.2,
        "total_duration_seconds": 14400
    }
    """
    from pathlib import Path
    from datetime import datetime, time
    import os
    
    camera_id = request.GET.get('camera_id')
    date_str = request.GET.get('date')
    start_time_str = request.GET.get('start_time')
    end_time_str = request.GET.get('end_time')
    
    if not camera_id or not date_str:
        return Response(
            {"error": "camera_id e date são obrigatórios"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        camera = Camera.objects.get(id=camera_id, owner=request.user)
    except Camera.DoesNotExist:
        return Response(
            {"error": "Câmera não encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    recordings_path = Path(f"/recordings/cam_{camera_id}/{date_str}")
    
    if not recordings_path.exists():
        return Response({
            "camera_id": int(camera_id),
            "date": date_str,
            "recordings": [],
            "total_size_mb": 0,
            "total_duration_seconds": 0
        })
    
    recordings = []
    total_size = 0
    
    for file_path in sorted(recordings_path.glob("*.mp4")):
        file_time = file_path.stem
        
        if start_time_str or end_time_str:
            try:
                file_dt = datetime.strptime(file_time, "%H-%M-%S").time()
                if start_time_str:
                    start_t = datetime.strptime(start_time_str, "%H:%M").time()
                    if file_dt < start_t:
                        continue
                if end_time_str:
                    end_t = datetime.strptime(end_time_str, "%H:%M").time()
                    if file_dt > end_t:
                        continue
            except ValueError:
                continue
        
        size_bytes = file_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        total_size += size_mb
        
        recordings.append({
            "filename": file_path.name,
            "start_time": file_time.replace("-", ":"),
            "size_mb": round(size_mb, 2),
            "playback_url": f"/cam_{camera_id}/{date_str}/{file_path.name}/index.m3u8"
        })
    
    return Response({
        "camera_id": int(camera_id),
        "date": date_str,
        "recordings": recordings,
        "total_size_mb": round(total_size, 2),
        "total_duration_seconds": len(recordings) * 3600
    })