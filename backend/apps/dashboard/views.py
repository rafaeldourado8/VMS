from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.http import StreamingHttpResponse
from apps.cameras.models import Camera
from apps.deteccoes.models import Deteccao
from django.utils import timezone
from datetime import timedelta
import json
import time

class DashboardStatsAPIView(APIView):
    """
    Endpoint mínimo para Dashboard - MVP (sem autenticação)
    """

    def get(self, request):
        # Stats básicas para o MVP
        total_cameras = Camera.objects.count()
        active_cameras = Camera.objects.filter(status='online').count()
        
        # Detecções das últimas 24h
        last_24h = timezone.now() - timedelta(hours=24)
        recent_detections = Deteccao.objects.filter(timestamp__gte=last_24h).count()
        
        return Response({
            "total_cameras": total_cameras,
            "active_cameras": active_cameras,
            "total_detections": recent_detections,
            "period": "24h"
        })


def dashboard_event_stream():
    """SSE stream for real-time dashboard updates"""
    while True:
        try:
            total_cameras = Camera.objects.count()
            online_cameras = Camera.objects.filter(status='online').count()
            offline_cameras = total_cameras - online_cameras
            
            last_24h = timezone.now() - timedelta(hours=24)
            detections_24h = Deteccao.objects.filter(timestamp__gte=last_24h).count()
            
            # Detections by type
            detections_by_type = {}
            for det in Deteccao.objects.filter(timestamp__gte=last_24h).values('vehicle_type'):
                vtype = det['vehicle_type'] or 'unknown'
                detections_by_type[vtype] = detections_by_type.get(vtype, 0) + 1
            
            # Recent activity
            recent_activity = []
            for det in Deteccao.objects.select_related('camera').order_by('-timestamp')[:5]:
                recent_activity.append({
                    'id': det.id,
                    'plate': det.plate_number or 'Sem placa',
                    'camera': det.camera.name if det.camera else 'Desconhecida',
                    'time': det.timestamp.isoformat()
                })
            
            data = {
                'total_cameras': total_cameras,
                'cameras_status': {
                    'online': online_cameras,
                    'offline': offline_cameras
                },
                'detections_24h': detections_24h,
                'detections_by_type': detections_by_type,
                'recent_activity': recent_activity,
                'alerts': 0
            }
            
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(2)
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
            time.sleep(5)


@api_view(['GET'])
def dashboard_stream(request):
    """SSE endpoint for real-time dashboard updates"""
    response = StreamingHttpResponse(
        dashboard_event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response