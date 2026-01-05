from dataclasses import dataclass
from typing import Optional
from enum import Enum
from ..value_objects.stream_path import StreamPath
from ..value_objects.hls_url import HLSUrl


class StreamStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


@dataclass
class Stream:
    """Entidade de domínio Stream"""
    
    camera_id: int
    rtsp_url: str
    path: StreamPath
    hls_url: HLSUrl
    status: StreamStatus = StreamStatus.INACTIVE
    viewers: int = 0
    on_demand: bool = True
    
    def start(self) -> None:
        """Inicia o stream"""
        self.status = StreamStatus.ACTIVE
    
    def stop(self) -> None:
        """Para o stream"""
        self.status = StreamStatus.INACTIVE
        self.viewers = 0
    
    def mark_error(self) -> None:
        """Marca stream com erro"""
        self.status = StreamStatus.ERROR
    
    def is_active(self) -> bool:
        """Verifica se o stream está ativo"""
        return self.status == StreamStatus.ACTIVE
    
    def add_viewer(self) -> None:
        """Adiciona um viewer"""
        self.viewers += 1
    
    def remove_viewer(self) -> None:
        """Remove um viewer"""
        if self.viewers > 0:
            self.viewers -= 1
