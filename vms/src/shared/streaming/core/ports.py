from typing import Protocol, Optional
from shared.streaming.recording.models import RecordingSession, RecordingStatus

class RecordingPort(Protocol):
    def start(self, stream_id: str) -> None:
        """Inicia gravação para um stream"""
        ...
    
    def stop(self, stream_id: str) -> None:
        """Para gravação de um stream"""
        ...
    
    def status(self, stream_id: str) -> Optional[RecordingStatus]:
        """Retorna status da gravação"""
        ...
