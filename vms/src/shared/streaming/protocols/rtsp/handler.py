from ..protocol_handler import ProtocolHandler

class RTSPHandler(ProtocolHandler):
    
    def validate_url(self, url: str) -> bool:
        return url.startswith('rtsp://')
    
    def normalize_url(self, url: str) -> str:
        return url.strip()
    
    def get_protocol_name(self) -> str:
        return 'RTSP'
