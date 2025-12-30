from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Clip, Mosaico
from .serializers import ClipSerializer, MosaicoSerializer, ClipCreateSerializer
from .services import ClipService

class ClipViewSet(viewsets.ModelViewSet):
    serializer_class = ClipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Clip.objects.filter(owner=self.request.user)

    def create(self, request):
        serializer = ClipCreateSerializer(data=request.data)
        if serializer.is_valid():
            clip = ClipService.create_clip(
                user=request.user,
                **serializer.validated_data
            )
            return Response(ClipSerializer(clip).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MosaicoViewSet(viewsets.ModelViewSet):
    serializer_class = MosaicoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Mosaico.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def update_cameras(self, request, pk=None):
        mosaico = self.get_object()
        camera_positions = request.data.get('cameras', [])
        
        # Limpar posições existentes
        mosaico.mosaicoCameraPosition_set.all().delete()
        
        # Adicionar novas posições (máximo 4)
        for pos_data in camera_positions[:4]:
            from .models import MosaicoCameraPosition
            from apps.cameras.models import Camera
            
            camera = get_object_or_404(Camera, id=pos_data['camera_id'], owner=request.user)
            MosaicoCameraPosition.objects.create(
                mosaico=mosaico,
                camera=camera,
                position=pos_data['position']
            )
        
        return Response(MosaicoSerializer(mosaico).data)