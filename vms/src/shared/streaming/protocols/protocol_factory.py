from .protocol_handler import ProtocolHandler
from .rtsp.handler import RTSPHandler
from .rtmp.handler import RTMPHandler
from .ip.handler import IPHandler
from .p2.handler import P2Handler

class ProtocolFactory:
    
    _handlers = {
        'RTSP': RTSPHandler(),
        'RTMP': RTMPHandler(),
        'IP': IPHandler(),
        'P2P': P2Handler(),
    }
    
    @classmethod
    def get_handler(cls, protocol: str) -> ProtocolHandler:
        handler = cls._handlers.get(protocol.upper())
        if not handler:
            raise ValueError(f"Unsupported protocol: {protocol}")
        return handler
    
    @classmethod
    def detect_protocol(cls, url: str) -> ProtocolHandler:
        for handler in cls._handlers.values():
            if handler.validate_url(url):
                return handler
        raise ValueError(f"Could not detect protocol from URL: {url}")
