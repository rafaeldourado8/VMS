import time
import httpx
from django.core.management.base import BaseCommand
from apps.clips.models import Clip

CLIPS_SERVICE_URL = "http://clips:8004"

class Command(BaseCommand):
    help = 'Processa clips pendentes'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando processamento de clips...')
        
        while True:
            pending_clips = Clip.objects.filter(status='pending')
            
            for clip in pending_clips:
                try:
                    self.stdout.write(f'Processando clip {clip.id}...')
                    
                    with httpx.Client(timeout=10.0) as client:
                        response = client.post(
                            f"{CLIPS_SERVICE_URL}/clips/create",
                            json={
                                "camera_id": clip.camera_id_backup,
                                "start_time": clip.start_time.isoformat(),
                                "end_time": clip.end_time.isoformat(),
                                "quality": "medium"
                            }
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            clip.external_id = data.get("id")
                            clip.file_path = f"/clips/{data.get('id')}.mp4"
                            clip.status = 'processing'
                            clip.save()
                            self.stdout.write(self.style.SUCCESS(f'Clip {clip.id} enviado'))
                        else:
                            self.stdout.write(self.style.ERROR(f'Erro: {response.text}'))
                            
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Erro: {e}'))
            
            processing_clips = Clip.objects.filter(status='processing')
            for clip in processing_clips:
                if clip.external_id:
                    try:
                        with httpx.Client(timeout=5.0) as client:
                            response = client.get(f"{CLIPS_SERVICE_URL}/clips/{clip.external_id}")
                            if response.status_code == 200:
                                data = response.json()
                                if data.get('status') == 'completed':
                                    clip.status = 'completed'
                                    clip.save()
                                    self.stdout.write(self.style.SUCCESS(f'Clip {clip.id} concluído'))
                                elif data.get('status') == 'failed':
                                    clip.status = 'failed'
                                    clip.save()
                    except:
                        pass
            
            time.sleep(5)
