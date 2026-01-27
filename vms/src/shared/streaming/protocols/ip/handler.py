from ..protocol_handler import ProtocolHandler

class IPHandler(ProtocolHandler):
    
    def validate_url(self, url: str) -> bool:
        return url.startswith('http://') or url.startswith('https://')
    
    def normalize_url(self, url: str) -> str:
        return url.strip()
    
    def get_protocol_name(self) -> str:
        return 'IP'
