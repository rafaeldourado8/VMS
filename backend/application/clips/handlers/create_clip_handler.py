from ..commands.create_clip_command import CreateClipCommand
from datetime import datetime

from domain.clips import Clip, ClipRepository

class CreateClipHandler:
    """Handler para criar clip de vídeo"""
    
    def __init__(self, repository: ClipRepository):
        self.repository = repository
    
    def handle(self, command: CreateClipCommand) -> Clip:
        """Executa o comando de criar clip"""
        
        duration = int((command.end_time - command.start_time).total_seconds())
        
        clip = Clip(
            id=None,
            owner_id=command.owner_id,
            camera_id=command.camera_id,
            name=command.name,
            start_time=command.start_time,
            end_time=command.end_time,
            file_path=command.file_path,
            thumbnail_path=command.thumbnail_path,
            duration_seconds=duration,
            created_at=datetime.now()
        )
        
        return self.repository.create_clip(clip)