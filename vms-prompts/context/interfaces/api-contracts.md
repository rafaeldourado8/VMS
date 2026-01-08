# API Contracts

## Inter-Service Communication

### Django -> Streaming Service
```
POST /streams/{camera_id}/start
Body: {"rtsp_url": str, "webrtc_enabled": bool}
Response: {"status": "started", "path": str}
```

### Streaming Service -> AI Service (via RabbitMQ)
```
Exchange: ai.frames
Routing: camera.{camera_id}
Payload: {"camera_id": str, "timestamp": iso8601, "frame": base64}
```

### AI Service -> Django (via RabbitMQ)
```
Exchange: events
Routing: detection.completed
Payload: {"camera_id": str, "result": DetectionResult}
```

## Client API (via Kong)

### WebRTC Viewer
```
WS /stream/camera/{id}/webrtc
Protocol: WHEP
```

### HLS Fallback
```
GET /stream/camera/{id}/hls/index.m3u8
```
