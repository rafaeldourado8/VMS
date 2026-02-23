import httpx
from datetime import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.cameras.models import Camera
from .models import Clip

CLIPS_SERVICE_URL = "http://clips:8004"

class ClipService:
    @staticmethod
    def create_clip(user, camera_id, name, start_time, end_time, quality="medium"):
        """Cria um clip de vídeo via Clips Service"""
        camera = get_object_or_404(Camera, id=camera_id, owner=user)
        
        duration = int((end_time - start_time).total_seconds())
        
        # Criar registro no banco primeiro com backup de informações da câmera
        clip = Clip.objects.create(
            owner=user,
            camera=camera,
            camera_id_backup=camera.id,
            camera_name_backup=camera.name,
            name=name,
            start_time=start_time,
            end_time=end_time,
            file_path=f"/clips/pending_{camera_id}_{int(start_time.timestamp())}.mp4",
            duration_seconds=duration,
            status='pending',
            is_protected=True  # Protegido contra retenção
        )
        
        # Tentar criar no serviço de clips (assíncrono)
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.post(
                    f"{CLIPS_SERVICE_URL}/clips/create",
                    json={
                        "camera_id": camera_id,
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "quality": quality
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    clip.external_id = data.get("id")
                    clip.file_path = f"/clips/{data.get('id')}.mp4"
                    clip.status = 'processing'
                    clip.save()
        except Exception as e:
            print(f"[ClipService] Erro ao chamar serviço: {e}")
            # Mantém o clip como pending
        
        return clip
    
    @staticmethod
    def get_clip_status(clip_id):
        """Verifica status do clip no serviço"""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{CLIPS_SERVICE_URL}/clips/{clip_id}")
                if response.status_code == 200:
                    return response.json()
        except:
            pass
        return None
    
    @staticmethod
    def get_download_url(clip_id):
        """Retorna URL de download do clip"""
        return f"{CLIPS_SERVICE_URL}/clips/{clip_id}/download"