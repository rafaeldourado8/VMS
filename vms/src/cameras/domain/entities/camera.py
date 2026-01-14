from dataclasses import dataclass

@dataclass
class Camera:
    id: str
    name: str
    stream_url: str
    city_id: str
    type: str = None  # Auto-detectado
    status: str = 'inactive'
    lpr_enabled: bool = False
    
    def __post_init__(self):
        if self.type is None:
            self.type = self._detect_type()
        self.lpr_enabled = self.type == 'rtsp'
    
    def _detect_type(self) -> str:
        """Detecta tipo pela URL: rtsp:// = LPR, rtmp:// = Bullet"""
        if self.stream_url.startswith('rtsp://'):
            return 'rtsp'
        elif self.stream_url.startswith('rtmp://'):
            return 'rtmp'
        raise ValueError(f"Invalid stream URL: {self.stream_url}")
    
    def activate(self):
        self.status = 'active'
    
    def deactivate(self):
        self.status = 'inactive'
    
    def is_lpr_enabled(self) -> bool:
        return self.lpr_enabled
    
    def is_active(self) -> bool:
        return self.status == 'active'
