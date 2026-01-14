from enum import Enum


class Permission(str, Enum):
    """Permissões do sistema."""
    
    # Câmeras
    VIEW_CAMERAS = "view_cameras"
    MANAGE_CAMERAS = "manage_cameras"
    
    # Detecções
    VIEW_DETECTIONS = "view_detections"
    
    # Blacklist
    MANAGE_BLACKLIST = "manage_blacklist"
    
    # Gravações
    VIEW_RECORDINGS = "view_recordings"
    CREATE_CLIPS = "create_clips"
    
    # Admin total
    ADMIN_ALL = "admin_all"
    
    def __str__(self) -> str:
        return self.value
