from rest_framework.decorators import action
from rest_framework.response import Response
from pathlib import Path
from .models import Clip

# Adicionar ao ClipViewSet em views.py

@action(detail=False, methods=['get'])
def protected_files(self, request):
    """Retorna lista de arquivos de clips protegidos para retenção"""
    clips = Clip.objects.filter(is_protected=True, status='completed')
    
    protected_files = []
    for clip in clips:
        if clip.file_path and Path(clip.file_path).exists():
            protected_files.append(str(Path(clip.file_path).resolve()))
    
    return Response({'protected_files': protected_files})
