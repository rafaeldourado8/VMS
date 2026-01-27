from typing import Optional, Dict
from shared.streaming.core.ports import RecordingPort
from shared.streaming.recording.models import RecordingStatus

class MockRecordingAdapter:
    """Mock adapter - apenas salva estado em memória"""
    
    def __init__(self):
        self._recordings: Dict[str, RecordingStatus] = {}
    
    def start(self, stream_id: str) -> None:
        self._recordings[stream_id] = RecordingStatus.ON
    
    def stop(self, stream_id: str) -> None:
        if stream_id in self._recordings:
            self._recordings[stream_id] = RecordingStatus.OFF
    
    def status(self, stream_id: str) -> Optional[RecordingStatus]:
        return self._recordings.get(stream_id)
