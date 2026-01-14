from abc import ABC, abstractmethod


class IRecordingService(ABC):
    @abstractmethod
    async def start_recording(self, camera_id: str, stream_url: str) -> str:
        pass
    
    @abstractmethod
    async def stop_recording(self, camera_id: str) -> None:
        pass
