from abc import ABC, abstractmethod
from domain.entities.stream import Stream

class IStreamRepository(ABC):
    @abstractmethod
    def save(self, stream: Stream) -> None:
        pass
    
    @abstractmethod
    def find_by_camera_id(self, camera_id: str) -> Stream | None:
        pass
    
    @abstractmethod
    def list_active(self) -> list[Stream]:
        pass
    
    @abstractmethod
    def delete(self, stream_id: str) -> None:
        pass
