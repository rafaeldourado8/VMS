# MediaMTX Service Context

## Role
Central media server for all RTSP, WebRTC, and HLS operations.

## API Endpoints Used
- GET /v3/paths - List active streams
- POST /v3/config/paths/{name} - Add stream source
- DELETE /v3/config/paths/{name} - Remove stream
- GET /v3/paths/{name} - Stream status and viewers

## Configuration Location
`/etc/mediamtx/mediamtx.yml`

## Stream Path Convention
`camera/{camera_id}` - Live camera streams
`playback/{recording_id}` - On-demand playback

## Health Check
GET /v3/paths returns 200 if operational.

## Restart Behavior
Streams auto-reconnect. Django polls status every 30s.
