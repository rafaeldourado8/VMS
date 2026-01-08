# Streaming Service Context

## Role
FastAPI service for stream management and frame extraction.

## Responsibilities
- Proxy WebRTC signaling
- Extract JPEG frames from streams
- Push frames to AI queue
- Monitor stream health

## Endpoints
- POST /streams/{camera_id}/start - Initialize stream
- DELETE /streams/{camera_id}/stop - Terminate stream
- GET /streams/{camera_id}/frame - Single frame capture
- WS /streams/{camera_id}/webrtc - WebRTC signaling

## Frame Extraction
Uses FFmpeg subprocess: `ffmpeg -i rtsp://mediamtx/camera/{id} -frames:v 1 -f image2 -`

## Queue Publishing
Publishes to `ai.frames` exchange with routing key `camera.{id}`.
