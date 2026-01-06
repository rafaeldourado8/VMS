import os
import subprocess
from datetime import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.cameras.models import Camera
from .models import Clip

class ClipService:
    @staticmethod
    def create_clip(user, camera_id, name, start_time, end_time):
        """Cria um clip de vídeo a partir de uma gravação"""
        camera = get_object_or_404(Camera, id=camera_id, owner=user)
        
        # Calcular duração
        duration = (end_time - start_time).total_seconds()
        
        # Gerar paths
        clips_dir = os.path.join(settings.MEDIA_ROOT, 'clips', str(user.id))
        os.makedirs(clips_dir, exist_ok=True)
        
        filename = f"{camera.name}_{start_time.strftime('%Y%m%d_%H%M%S')}.mp4"
        file_path = os.path.join(clips_dir, filename)
        thumbnail_path = os.path.join(clips_dir, f"{filename}_thumb.jpg")
        
        # Extrair clip usando ffmpeg (simulado - implementar com gravações reais)
        # ffmpeg_cmd = [
        #     'ffmpeg', '-i', f'path_to_recording_{camera_id}',
        #     '-ss', start_time.strftime('%H:%M:%S'),
        #     '-t', str(int(duration)),
        #     '-c', 'copy', file_path
        # ]
        # subprocess.run(ffmpeg_cmd)
        
        # Por agora, criar arquivo vazio para teste
        with open(file_path, 'w') as f:
            f.write('')
        
        clip = Clip.objects.create(
            owner=user,
            camera=camera,
            name=name,
            start_time=start_time,
            end_time=end_time,
            file_path=file_path,
            thumbnail_path=thumbnail_path,
            duration_seconds=int(duration)
        )
        
        return clip