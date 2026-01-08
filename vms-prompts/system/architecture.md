# VMS Architecture Reference

## Service Map
```
[Cameras] -> [MediaMTX] -> [Streaming Service (FastAPI)]
                |                    |
                v                    v
           [FFmpeg] ---------> [Django Backend]
                                     |
                    +----------------+----------------+
                    v                v                v
              [Kong API]      [AI Service]     [RabbitMQ]
                    |              |                |
                    v              v                v
              [HAProxy]    [AWS Rekognition]   [Workers]
```

## Port Assignments
- MediaMTX: 8554 (RTSP), 8889 (WebRTC), 8888 (HLS)
- Django: 8000
- Streaming Service: 8001
- AI Service: 8002
- Kong: 8080
- PostgreSQL: 5432
- Redis: 6379
- RabbitMQ: 5672

## Data Flow Rules
- Video never passes through Django
- AI receives frames from Streaming Service via queue
- Playback reads from storage, not MediaMTX
