"""
VMS - Detection Views (DDD)
===========================
Endpoints REST delegando para handlers da camada de aplicação.
"""

import base64
import time
from datetime import datetime

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

# Imports para WebSocket e Channels
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .serializers import DeteccaoSerializer, IngestDeteccaoSerializer
from .permissions import HasIngestAPIKey
from infrastructure.persistence.django.repositories import DjangoDetectionRepository, DjangoCameraRepository
from application.detection.handlers import (
    ListDetectionsHandler, GetDetectionHandler, GetDetectionQuery, ProcessDetectionHandler
)
from application.detection.queries.list_detections_query import ListDetectionsQuery
from application.detection.commands.process_detection_command import ProcessDetectionCommand

# Import direto do Model para a ingestão rápida (Bypass momentâneo do DDD puro para performance)
from apps.deteccoes.models import Deteccao

class DeteccaoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeteccaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        detection_repo = DjangoDetectionRepository()
        camera_repo = DjangoCameraRepository()
        self.list_handler = ListDetectionsHandler(detection_repo, camera_repo)
        self.get_handler = GetDetectionHandler(detection_repo, camera_repo)

    def get_queryset(self):
        camera_id = self.request.query_params.get("camera_id")
        plate = self.request.query_params.get("plate")
        
        query = ListDetectionsQuery(
            owner_id=self.request.user.id,
            camera_id=int(camera_id) if camera_id else None,
            plate=plate,
            limit=100
        )
        detections = self.list_handler.handle(query)
        
        return Deteccao.objects.filter(id__in=[d.id for d in detections])

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        query = GetDetectionQuery(detection_id=int(kwargs['pk']), owner_id=request.user.id)
        try:
            detection = self.get_handler.handle(query)
            detection_model = Deteccao.objects.get(id=detection.id)
            serializer = self.get_serializer(detection_model)
            return Response(serializer.data)
        except ValueError:
            return Response({"detail": "Não encontrado."}, status=status.HTTP_404_NOT_FOUND)

class IngestDeteccaoAPIView(APIView):
    permission_classes = [HasIngestAPIKey]
    authentication_classes = []
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        detection_repo = DjangoDetectionRepository()
        self.process_handler = ProcessDetectionHandler(detection_repo)

    def post(self, request):
        image_url = None
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            camera_id = request.data.get('camera_id', 'unknown')
            filename = f"detections/cam_{camera_id}_{timestamp}.jpg"
            path = default_storage.save(filename, ContentFile(image_file.read()))
            image_url = default_storage.url(path)
        
        data = request.data.copy()
        if image_url:
            data['image_url'] = image_url
        
        serializer = IngestDeteccaoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        command = ProcessDetectionCommand(**serializer.validated_data)
        detection = self.process_handler.handle(command)
        
        detection_model = Deteccao.objects.get(id=detection.id)
        response_data = DeteccaoSerializer(detection_model).data
        return Response(response_data, status=status.HTTP_201_CREATED)

class FastIngestDeteccaoView(APIView):
    """
    Endpoint otimizado para o serviço de IA interno.
    Recebe JSON com imagem em Base64, salva e dispara WebSocket.
    """
    # Permitir acesso interno (idealmente limitar por IP ou Token interno no futuro)
    permission_classes = [permissions.AllowAny] 
    authentication_classes = []
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            data = request.data
            camera_id = data.get('camera_id')
            plate_number = data.get('plate_number')
            confidence = data.get('confidence', 0.0)
            image_b64 = data.get('image_base64')
            timestamp_str = data.get('timestamp')

            if not all([camera_id, plate_number, image_b64]):
                return Response({"error": "Dados incompletos"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Filtro de confiança mínima (50% para monitoramento de trânsito)
            if confidence < 0.5:
                return Response({"status": "rejected", "reason": "confidence_too_low"}, status=status.HTTP_200_OK)

            # 1. Decodificar e Salvar Imagem
            try:
                format, imgstr = image_b64.split(';base64,') if ';base64,' in image_b64 else (None, image_b64)
                ext = format.split('/')[-1] if format else 'jpg'
                image_data = base64.b64decode(imgstr)
                
                file_name = f"detections/ai_cam{camera_id}_{plate_number}_{int(time.time())}.{ext}"
                content_file = ContentFile(image_data, name=file_name)
            except Exception as e:
                return Response({"error": f"Erro ao decodificar imagem: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # 2. Salvar no Banco de Dados (Usando o Model Django diretamente)
            # Isso garante persistência antes de avisar o front
            deteccao = Deteccao.objects.create(
                camera_id=camera_id,
                plate=plate_number,
                confidence=confidence,
                timestamp=timestamp_str if timestamp_str else datetime.now(),
                image_url=f"data:image/jpeg;base64,{imgstr}"  # Salva como data URL
            )

            # 3. Disparar WebSocket (Broadcasting)
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    "detections_group",  # Grupo definido no Consumer do Channels
                    {
                        "type": "send_detection",
                        "message": {
                            "id": str(deteccao.id),
                            "camera_id": deteccao.camera_id,
                            "plate": deteccao.plate,
                            "confidence": float(deteccao.confidence),
                            "timestamp": deteccao.timestamp.isoformat(),
                            "method": "AI_YOLO_OCR",
                            "image": imgstr, 
                            "metadata": {
                                "votes": 1,
                                "total": 1,
                                "frames_analyzed": 1
                            }
                        }
                    }
                )

            return Response({"status": "processed", "id": deteccao.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Erro no FastIngest: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)