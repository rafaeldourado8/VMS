from dataclasses import dataclass


@dataclass
class GetStreamStatusQuery:
    """Query para obter status de um stream"""
    
    camera_id: int
