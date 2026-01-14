from enum import Enum

class CameraType(Enum):
    RTSP = 'rtsp'  # LPR (max 20 por cidade)
    RTMP = 'rtmp'  # Bullet (max 1000 por cidade)
    
    def is_lpr_enabled(self) -> bool:
        return self == CameraType.RTSP
    
    @property
    def display_name(self) -> str:
        return {
            CameraType.RTSP: 'RTSP (LPR)',
            CameraType.RTMP: 'RTMP (Bullet)'
        }[self]
