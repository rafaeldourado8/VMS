from typing import Optional
from shared.streaming.recording.models import RecordingStatus
from infrastructure.servers.mediamtx.adapter import MediaMTXAdapter

class MediaMTXRecordingAdapter:
    """Adapter real - MediaMTX grava automaticamente via pathDefaults"""
    
    def __init__(self, mediamtx: MediaMTXAdapter):
        self.mediamtx = mediamtx
    
    def start(self, stream_id: str) -> None:
        """MediaMTX já grava automaticamente (record: yes global)"""
        pass
    
    def stop(self, stream_id: str) -> None:
        """MediaMTX para automaticamente quando fonte desconecta"""
        pass
    
    def status(self, stream_id: str) -> Optional[RecordingStatus]:
        """Verifica se path existe (ONLINE) ou não (OFFLINE)"""
        path_info = self.mediamtx.get_path(stream_id)
        if not path_info:
            return None  # Câmera OFFLINE
        return RecordingStatus.ON  # MediaMTX grava automaticamente
