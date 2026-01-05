from dataclasses import dataclass


@dataclass
class DeleteCameraCommand:
    """Command para deletar uma câmera"""
    
    camera_id: int
    owner_id: int
