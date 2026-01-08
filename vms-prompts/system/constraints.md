# VMS Constraints

## Forbidden
- No GStreamer, nginx-rtmp, or alternative media servers
- No Flask, no Express, no alternative web frameworks
- No MongoDB, no Kafka
- No direct cloud calls from Django
- No video processing in Python (FFmpeg only)
- No synchronous AI inference in request cycle

## Required Patterns
- Repository pattern for data access
- Service layer between API and domain
- Event-driven for cross-domain communication
- Interface abstraction for all external providers

## Performance Boundaries
- WebRTC latency < 500ms
- Frame extraction < 100ms
- AI queue processing < 2s per frame
- API response < 200ms (excluding streaming)
