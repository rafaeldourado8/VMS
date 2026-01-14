from streaming.domain.services.recording_service import IRecordingService


class FFmpegRecorderStub(IRecordingService):
    def __init__(self):
        self.active = {}
    
    async def start_recording(self, camera_id: str, stream_url: str) -> str:
        path = f"/recordings/{camera_id}"
        self.active[camera_id] = {"url": stream_url, "path": path}
        return path
    
    async def stop_recording(self, camera_id: str) -> None:
        if camera_id in self.active:
            del self.active[camera_id]
