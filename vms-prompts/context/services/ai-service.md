# AI Service Context

## Role
FastAPI service for detection processing and provider abstraction.

## Responsibilities
- Consume frames from queue
- Route to configured provider
- Store results in PostgreSQL
- Publish detection events

## Endpoints
- POST /detect - Synchronous detection (internal use only)
- GET /detections - Query results
- GET /providers - List available providers

## Provider Architecture
```python
class DetectionProvider(Protocol):
    async def detect(self, frame: bytes, config: ProviderConfig) -> DetectionResult: ...
    def get_capabilities(self) -> list[str]: ...
```

## Current Providers
- `RekognitionProvider` - AWS Rekognition (active)
- `YOLOProvider` - Local YOLO (placeholder)

## Cost Control
- Rate limit: max 5 frames/second per camera
- Batch mode: collect frames, process on interval
- Skip identical frames (perceptual hash)
