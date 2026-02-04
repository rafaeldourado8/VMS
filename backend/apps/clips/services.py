import httpx
from datetime import datetime
from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.cameras.models import Camera
from .models import Clip

CLIPS_SERVICE_URL = "http://clips:8004"

class ClipService:
    @staticmethod
    async def create_clip(user, camera_id, name, start_time, end_time, quality="medium"):
        """Cria um clip de vídeo via Clips Service"""
        camera = get_object_or_404(Camera, id=camera_id, owner=user)
        
        duration = int((end_time - start_time).total_seconds())
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CLIPS_SERVICE_URL}/clips/create",
                json={
                    "camera_id": camera_id,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "quality": quality
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Erro ao criar clip: {response.text}")
            
            data = response.json()
            clip_id = data["id"]
        
        clip = Clip.objects.create(
            owner=user,
            camera=camera,
            name=name,
            start_time=start_time,
            end_time=end_time,
            file_path=f"/clips/{clip_id}.mp4",
            duration_seconds=duration
        )
        
        clip.external_id = clip_id
        clip.save()
        
        return clip
    
    @staticmethod
    async def get_clip_status(clip_id):
        """Verifica status do clip no serviço"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CLIPS_SERVICE_URL}/clips/{clip_id}")
            if response.status_code == 200:
                return response.json()
        return None
    
    @staticmethod
    def get_download_url(clip_id):
        """Retorna URL de download do clip"""
        return f"{CLIPS_SERVICE_URL}/clips/{clip_id}/download"