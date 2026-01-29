from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models_lpr import LPRDetection
from apps.cameras.models import Camera
import redis
import json
import logging

logger = logging.getLogger(__name__)

class LPRDetectionSerializer(serializers.ModelSerializer):
    camera_name = serializers.CharField(source='camera.name', read_only=True)
    plate_image_url = serializers.SerializerMethodField()
    full_frame_url = serializers.SerializerMethodField()
    
    class Meta:
        model = LPRDetection
        fields = ['id', 'camera', 'camera_name', 'plate_text', 'confidence', 
                  'bbox', 'plate_id', 'timestamp', 'is_mercosul', 
                  'plate_image_url', 'full_frame_url', 'metadata']
        read_only_fields = ['id', 'timestamp']
    
    def get_plate_image_url(self, obj):
        return f"/snapshots/{obj.plate_image_path}"
    
    def get_full_frame_url(self, obj):
        return f"/snapshots/{obj.full_frame_path}"


@api_view(['POST'])
@permission_classes([])
def ingest_lpr(request):
    """Endpoint para LPR service enviar detecções"""
    try:
        data = request.data
        camera = Camera.objects.get(id=data['camera_id'])
        
        LPRDetection.objects.create(
            camera=camera,
            plate_text=data['plate_text'],
            confidence=data['confidence'],
            bbox=data['bbox'],
            plate_id=data['plate_id'],
            plate_image_path=data['plate_image_path'],
            full_frame_path=data['full_frame_path'],
            is_mercosul=data.get('is_mercosul', False),
            metadata=data.get('metadata', {})
        )
        
        return Response({'success': True}, status=201)
    except Exception as e:
        logger.error(f"Erro ao ingerir LPR: {e}")
        return Response({'error': str(e)}, status=400)


class LPRViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para detecções LPR"""
    serializer_class = LPRDetectionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        cameras = Camera.objects.filter(owner=user)
        queryset = LPRDetection.objects.filter(camera__in=cameras)
        
        # Filtros
        plate_text = self.request.query_params.get('plate_text')
        camera_id = self.request.query_params.get('camera_id')
        mercosul_only = self.request.query_params.get('mercosul_only')
        
        if plate_text:
            queryset = queryset.filter(plate_text__icontains=plate_text)
        if camera_id:
            queryset = queryset.filter(camera_id=camera_id)
        if mercosul_only == 'true':
            queryset = queryset.filter(is_mercosul=True)
        
        return queryset[:100]
    
    @action(detail=False, methods=['post'])
    def start_lpr(self, request):
        """Inicia LPR para uma câmera"""
        camera_id = request.data.get('camera_id')
        
        try:
            camera = Camera.objects.get(id=camera_id, owner=request.user)
        except Camera.DoesNotExist:
            return Response({'error': 'Câmera não encontrada'}, status=404)
        
        try:
            r = redis.Redis.from_url('redis://redis_cache:6379/2')
            payload = {
                'camera_id': camera.id,
                'input_stream': f'rtsp://mediamtx:8554/cam_{camera.id}',
                'output_rtsp': f'rtsp://mediamtx:8554/lpr_cam_{camera.id}'
            }
            r.publish('camera:provisioned', json.dumps(payload))
            
            logger.info(f"LPR iniciado para câmera {camera_id}")
            return Response({'success': True, 'message': f'LPR iniciado para {camera.name}'})
        except Exception as e:
            logger.error(f"Erro ao iniciar LPR: {e}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['post'])
    def stop_lpr(self, request):
        """Para LPR para uma câmera"""
        camera_id = request.data.get('camera_id')
        
        try:
            r = redis.Redis.from_url('redis://redis_cache:6379/2')
            r.publish('camera:removed', json.dumps({'camera_id': camera_id}))
            
            logger.info(f"LPR parado para câmera {camera_id}")
            return Response({'success': True, 'message': 'LPR parado'})
        except Exception as e:
            logger.error(f"Erro ao parar LPR: {e}")
            return Response({'error': str(e)}, status=500)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas de detecções LPR"""
        user = self.request.user
        cameras = Camera.objects.filter(owner=user)
        detections = LPRDetection.objects.filter(camera__in=cameras)
        
        return Response({
            'total_detections': detections.count(),
            'mercosul_detections': detections.filter(is_mercosul=True).count(),
            'unique_plates': detections.values('plate_text').distinct().count(),
            'cameras_with_lpr': detections.values('camera').distinct().count()
        })
