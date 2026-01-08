"""
VMS - Detection Views (DDD)
===========================
Endpoints REST delegando para handlers da camada de aplicação.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime

from .serializers import DeteccaoSerializer, IngestDeteccaoSerializer
from .permissions import HasIngestAPIKey
from infrastructure.persistence.django.repositories import DjangoDetectionRepository, DjangoCameraRepository
from application.detection.handlers import (
    ListDetectionsHandler, GetDetectionHandler, GetDetectionQuery, ProcessDetectionHandler
)
from application.detection.queries.list_detections_query import ListDetectionsQuery
from application.detection.commands.process_detection_command import ProcessDetectionCommand

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
        
        from apps.deteccoes.models import Deteccao
        return Deteccao.objects.filter(id__in=[d.id for d in detections])

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        query = GetDetectionQuery(detection_id=int(kwargs['pk']), owner_id=request.user.id)
        try:
            detection = self.get_handler.handle(query)
            from apps.deteccoes.models import Deteccao
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
        
        from apps.deteccoes.models import Deteccao
        detection_model = Deteccao.objects.get(id=detection.id)
        response_data = DeteccaoSerializer(detection_model).data
        return Response(response_data, status=status.HTTP_201_CREATED)
