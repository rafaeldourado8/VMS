from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.deteccoes.models import Deteccao
from apps.cameras.models import Camera


@api_view(['GET'])
def live_stats(request):
    """Estatísticas em tempo real das detecções."""
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    
    stats = {
        'total_today': Deteccao.objects.filter(data_hora__date=now.date()).count(),
        'last_hour': Deteccao.objects.filter(data_hora__gte=last_hour).count(),
        'cameras_active': Camera.objects.filter(
            deteccoes__data_hora__gte=last_hour
        ).distinct().count(),
        'recent_detections': []
    }
    
    # Últimas 10 detecções
    recent = Deteccao.objects.select_related('camera').order_by('-data_hora')[:10]
    stats['recent_detections'] = [
        {
            'id': d.id,
            'placa': d.placa,
            'camera_id': d.camera.id,
            'camera_name': d.camera.name,
            'confianca': d.confianca,
            'data_hora': d.data_hora.isoformat(),
            'snapshot_url': d.snapshot_url
        }
        for d in recent
    ]
    
    return Response(stats)


@api_view(['GET'])
def camera_stream_info(request, camera_id):
    """Informações do stream WebRTC para uma câmera."""
    try:
        camera = Camera.objects.get(id=camera_id)
    except Camera.DoesNotExist:
        return Response({'error': 'Câmera não encontrada'}, status=404)
    
    return Response({
        'camera_id': camera.id,
        'camera_name': camera.name,
        'webrtc_url': f'http://mediamtx:8889/cam_{camera_id}_ai/whep',
        'hls_url': f'http://mediamtx:8888/cam_{camera_id}/index.m3u8',
        'status': 'active' if camera.is_active else 'inactive'
    })
