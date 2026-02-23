from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from .models import Clip, Mosaico
from .serializers import ClipSerializer, MosaicoSerializer, ClipCreateSerializer
from .services import ClipService
import os

class ClipViewSet(viewsets.ModelViewSet):
    serializer_class = ClipSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Clip.objects.filter(owner=self.request.user)

    def create(self, request):
        print(f"[ClipViewSet] Recebendo request: {request.data}")
        serializer = ClipCreateSerializer(data=request.data)
        if serializer.is_valid():
            print(f"[ClipViewSet] Dados válidos: {serializer.validated_data}")
            try:
                clip = ClipService.create_clip(
                    user=request.user,
                    **serializer.validated_data
                )
                print(f"[ClipViewSet] Clip criado: {clip.id}")
                return Response(ClipSerializer(clip).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"[ClipViewSet] Erro ao criar clip: {e}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print(f"[ClipViewSet] Erros de validação: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def video(self, request, pk=None):
        clip = self.get_object()
        file_path = clip.file_path
        
        if not os.path.exists(file_path):
            return Response({"error": "Arquivo não encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        return FileResponse(open(file_path, 'rb'), content_type='video/mp4')
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def protected_files(self, request):
        """Retorna lista de arquivos protegidos (clips) para o retention service"""
        protected_clips = Clip.objects.filter(is_protected=True).values_list('file_path', flat=True)
        return Response({'protected_files': list(protected_clips)})

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