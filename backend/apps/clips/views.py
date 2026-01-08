from django.utils.dateparse import parse_datetime
from infrastructure.persistence.django.repositories.django_clip_repository import DjangoClipRepository
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from application.clips.commands.create_clip_command import CreateClipCommand
from application.clips.handlers.create_clip_handler import CreateClipHandler

class ClipAPIView(APIView):
    """API para clips usando DDD"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self):
        super().__init__()
        self._repository = DjangoClipRepository()
        self._create_handler = CreateClipHandler(self._repository)
    
    def get(self, request):
        """Lista clips do usuário"""
        clips = self._repository.get_clips_by_user(request.user.id)
        
        data = [
            {
                "id": clip.id,
                "name": clip.name,
                "camera_id": clip.camera_id,
                "start_time": clip.start_time,
                "end_time": clip.end_time,
                "duration_seconds": clip.duration_seconds,
                "file_path": clip.file_path,
                "thumbnail_path": clip.thumbnail_path,
                "created_at": clip.created_at
            }
            for clip in clips
        ]
        
        return Response(data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """Cria novo clip"""
        data = request.data
        
        try:
            start_time = parse_datetime(data.get('start_time'))
            end_time = parse_datetime(data.get('end_time'))
            
            if not start_time or not end_time:
                return Response(
                    {"error": "start_time e end_time são obrigatórios"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            command = CreateClipCommand(
                owner_id=request.user.id,
                camera_id=data.get('camera_id'),
                name=data.get('name', ''),
                start_time=start_time,
                end_time=end_time,
                file_path=data.get('file_path', ''),
                thumbnail_path=data.get('thumbnail_path')
            )
            
            clip = self._create_handler.handle(command)
            
            return Response(
                {
                    "id": clip.id,
                    "name": clip.name,
                    "duration_seconds": clip.duration_seconds,
                    "created_at": clip.created_at
                },
                status=status.HTTP_201_CREATED
            )
            
        except ValueError as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )