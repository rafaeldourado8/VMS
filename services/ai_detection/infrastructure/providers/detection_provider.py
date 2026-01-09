from typing import Protocol, Dict, Any, List


class DetectionProvider(Protocol):
    async def detect_labels(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        ...
    
    async def detect_faces(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        ...
