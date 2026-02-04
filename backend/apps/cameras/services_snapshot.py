import cv2
import logging
from pathlib import Path
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

class SnapshotCacheService:
    """Gera e cacheia snapshots estáticos de gravações."""
    
    @staticmethod
    def generate_snapshot(video_path: str, output_path: Path = None) -> bytes:
        """Extrai primeiro frame do vídeo como snapshot."""
        try:
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                raise Exception("Não foi possível ler frame do vídeo")
            
            # Redimensiona para thumbnail (320x180)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img.thumbnail((320, 180), Image.Resampling.LANCZOS)
            
            # Salva em buffer
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            
            # Salva em arquivo se especificado
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(buffer.getvalue())
                buffer.seek(0)
            
            return buffer.getvalue()
        
        except Exception as e:
            logger.error(f"Erro ao gerar snapshot de {video_path}: {e}")
            return None
    
    @staticmethod
    async def cache_recording_snapshot(recording_id: int) -> bool:
        """Gera e cacheia snapshot de uma gravação."""
        from apps.cameras.models_recording import Recording
        
        try:
            recording = await Recording.objects.aget(id=recording_id)
            
            if recording.snapshot_cached:
                logger.info(f"Snapshot já existe para recording {recording_id}")
                return True
            
            video_path = Path("/recordings") / recording.video_path.lstrip('/')
            if not video_path.exists():
                logger.error(f"Vídeo não encontrado: {video_path}")
                return False
            
            # Gera snapshot
            snapshot_bytes = SnapshotCacheService.generate_snapshot(str(video_path))
            if not snapshot_bytes:
                return False
            
            # Salva no model
            filename = f"rec_{recording_id}_{recording.started_at.strftime('%Y%m%d_%H%M%S')}.jpg"
            recording.snapshot_cached.save(filename, ContentFile(snapshot_bytes), save=True)
            
            logger.info(f"✅ Snapshot cacheado para recording {recording_id}")
            return True
        
        except Exception as e:
            logger.error(f"Erro ao cachear snapshot {recording_id}: {e}")
            return False
