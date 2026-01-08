# Persistent Decisions

## Architecture Decisions (Immutable)
- 2024-01: MediaMTX selected over nginx-rtmp for WebRTC support
- 2024-01: DDD adopted for Django to isolate domains
- 2024-02: FastAPI for streaming due to async requirements
- 2024-02: Frame-only AI processing to reduce bandwidth costs
- 2024-03: Detection provider interface defined for future YOLO

## Implementation Decisions (Append-only)
- Recording stored as HLS segments, not monolithic files
- FFmpeg runs as subprocess, not library binding
- Redis used for stream status cache, not database
- Celery for async tasks, not Django-Q

## Rejected Alternatives
- GStreamer: Complex Python bindings
- Kafka: Overkill for message volume
- MongoDB: No need for document store
- Synchronous AI: Blocks request cycle
