from ..protocol_handler import ProtocolHandler

class P2Handler(ProtocolHandler):
    
    def validate_url(self, url: str) -> bool:
        return url.startswith('p2p://') or 'p2p' in url.lower()
    
    def normalize_url(self, url: str) -> str:
        return url.strip()
    
    def get_protocol_name(self) -> str:
        return 'P2P'
