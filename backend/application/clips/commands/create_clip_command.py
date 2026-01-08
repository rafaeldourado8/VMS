from dataclasses import dataclass
from datetime import datetime

@dataclass
class CreateClipCommand:
    """Command para criar clip de vídeo"""
    
    owner_id: int
    camera_id: int
    name: str
    start_time: datetime
    end_time: datetime
    file_path: str
    thumbnail_path: str = None