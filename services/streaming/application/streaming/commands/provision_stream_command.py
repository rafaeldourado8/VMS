from dataclasses import dataclass


@dataclass
class ProvisionStreamCommand:
    """Command para provisionar um stream"""
    
    camera_id: int
    rtsp_url: str
    name: str
    on_demand: bool = True
