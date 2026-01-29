"""
API de Ingestão de Detecções
Endpoint para receber detecções do microsserviço de IA
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
from datetime import datetime
import logging

from apps.deteccoes.models import Deteccao
from apps.cameras.models import Camera

logger = logging.getLogger(__name__)


def validate_api_key(request):
    """Valida API Key do header."""
    api_key = request.headers.get('X-API-Key')
    expected_key = getattr(settings, 'INGEST_API_KEY', 'default_insecure_key_12345')
    
    if not api_key:
        return False, "API Key não fornecida"
    
    if api_key != expected_key:
        return False, "API Key inválida"
    
    return True, None


@api_view(['POST'])
@permission_classes([AllowAny])
def ingest_deteccao(request):
    """
    Endpoint de ingestão de detecções.
    
    POST /api/deteccoes/ingest/
    Headers:
        X-API-Key: {INGEST_API_KEY}
    Body:
        {
            "camera_id": 1,
            "placa": "ABC1234",
            "confianca": 0.95,
            "snapshot_path": "snapshots/2025/01/15/cam1_ABC1234_143022.jpg",
            "vehicle_type": "car",
            "data_hora": "2025-01-15T14:30:22.123456"
        }
    """
    
    # Valida API Key
    valid, error = validate_api_key(request)
    if not valid:
        logger.warning(f"❌ Tentativa de acesso não autorizada: {error}")
        return Response(
            {'error': error},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Valida dados obrigatórios
    required_fields = ['camera_id', 'placa', 'confianca', 'snapshot_path']
    missing_fields = [field for field in required_fields if field not in request.data]
    
    if missing_fields:
        return Response(
            {'error': f'Campos obrigatórios faltando: {", ".join(missing_fields)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Busca câmera
        camera_id = request.data['camera_id']
        try:
            camera = Camera.objects.get(id=camera_id)
        except Camera.DoesNotExist:
            return Response(
                {'error': f'Câmera {camera_id} não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Parse data_hora
        data_hora_str = request.data.get('data_hora')
        if data_hora_str:
            data_hora = datetime.fromisoformat(data_hora_str.replace('Z', '+00:00'))
        else:
            data_hora = timezone.now()
        
        # Cria detecção
        deteccao = Deteccao.objects.create(
            camera=camera,
            placa=request.data['placa'],
            confianca=float(request.data['confianca']),
            snapshot_path=request.data['snapshot_path'],
            vehicle_type=request.data.get('vehicle_type', 'unknown'),
            data_hora=data_hora
        )
        
        logger.info(
            f"✅ Detecção criada: ID={deteccao.id} | "
            f"Placa={deteccao.placa} | "
            f"Câmera={camera.name} | "
            f"Confiança={deteccao.confianca:.2f}"
        )
        
        return Response(
            {
                'id': deteccao.id,
                'placa': deteccao.placa,
                'confianca': deteccao.confianca,
                'snapshot_url': deteccao.snapshot_url,
                'data_hora': deteccao.data_hora.isoformat(),
                'message': 'Detecção registrada com sucesso'
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar detecção: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Erro interno: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_deteccoes(request):
    """
    Lista detecções com filtros opcionais.
    
    GET /api/deteccoes/list/?camera_id=1&placa=ABC&limit=10
    """
    
    # Filtros
    queryset = Deteccao.objects.select_related('camera')
    
    camera_id = request.query_params.get('camera_id')
    if camera_id:
        queryset = queryset.filter(camera_id=camera_id)
    
    placa = request.query_params.get('placa')
    if placa:
        queryset = queryset.filter(placa__icontains=placa)
    
    # Paginação
    limit = int(request.query_params.get('limit', 10))
    queryset = queryset[:limit]
    
    # Serializa
    data = [
        {
            'id': det.id,
            'camera_id': det.camera.id,
            'camera_name': det.camera.name,
            'placa': det.placa,
            'confianca': det.confianca,
            'vehicle_type': det.vehicle_type,
            'snapshot_url': det.snapshot_url,
            'data_hora': det.data_hora.isoformat(),
            'created_at': det.created_at.isoformat()
        }
        for det in queryset
    ]
    
    return Response({
        'count': len(data),
        'results': data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def deteccao_detail(request, pk):
    """
    Detalhes de uma detecção específica.
    
    GET /api/deteccoes/{id}/
    """
    try:
        deteccao = Deteccao.objects.select_related('camera').get(pk=pk)
    except Deteccao.DoesNotExist:
        return Response(
            {'error': 'Detecção não encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    data = {
        'id': deteccao.id,
        'camera': {
            'id': deteccao.camera.id,
            'name': deteccao.camera.name,
            'location': deteccao.camera.location
        },
        'placa': deteccao.placa,
        'confianca': deteccao.confianca,
        'vehicle_type': deteccao.vehicle_type,
        'snapshot_path': deteccao.snapshot_path,
        'snapshot_url': deteccao.snapshot_url,
        'data_hora': deteccao.data_hora.isoformat(),
        'created_at': deteccao.created_at.isoformat()
    }
    
    return Response(data)
