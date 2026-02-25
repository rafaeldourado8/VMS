from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from .models import Recording
from .serializers import RecordingSerializer
import httpx
import os
import re
from datetime import datetime

class RecordingViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer
    filterset_fields = ['camera_id', 'date', 'is_valid']
    
    @action(detail=False, methods=['get'])
    def by_camera(self, request):
        camera_id = request.query_params.get('camera_id')
        date = request.query_params.get('date')
        
        recordings = Recording.objects.filter(camera_id=camera_id)
        if date:
            recordings = recordings.filter(date=date)
        
        serializer = self.get_serializer(recordings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='hls-url')
    def hls_url(self, request):
        """Gera URL HLS via HAProxy para câmera e data"""
        camera_id = request.query_params.get('camera_id')
        date = request.query_params.get('date')
        
        if not camera_id or not date:
            return Response({'error': 'camera_id e date são obrigatórios'}, status=400)
        
        # URL via HAProxy (gateway unificado)
        hls_url = f"/vod/playlist/{camera_id}/{date}/index.m3u8"
        
        return Response({
            'hls_url': hls_url,
            'camera_id': int(camera_id),
            'date': date
        })
    
    @action(detail=False, methods=['post'])
    async def sync_from_service(self, request):
        """Sincroniza gravações do Recording Service"""
        camera_id = request.data.get('camera_id')
        date = request.data.get('date')
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://recording:8006/recordings/{camera_id}",
                params={"date": date}
            )
            data = response.json()
            
            for file_info in data['files']:
                Recording.objects.update_or_create(
                    camera_id=camera_id,
                    date=date,
                    file_name=file_info['name'],
                    defaults={
                        'file_path': file_info['path'],
                        'size_mb': file_info['size_mb']
                    }
                )
        
        return Response({"status": "synced"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_recording_access(request):
    """Valida acesso a gravação via nginx auth_request"""
    original_uri = request.headers.get('X-Original-URI', '')
    
    # Extrair camera_id da URI: /recordings/camera_1/2026-02-25/14-45-12.mp4
    match = re.match(r'/recordings/camera_(\d+)/', original_uri)
    if not match:
        return HttpResponse(status=403)
    
    camera_id = int(match.group(1))
    user = request.user
    
    # Validar permissão do usuário
    # TODO: Implementar lógica de permissão por câmera
    # Por enquanto: usuários autenticados podem acessar qualquer câmera
    
    if user.is_authenticated:
        return HttpResponse(status=200, headers={'X-User-Id': str(user.id)})
    
    return HttpResponse(status=403)
