from dataclasses import dataclass


@dataclass
class RemoveStreamCommand:
    """Command para remover um stream"""
    
    camera_id: int
