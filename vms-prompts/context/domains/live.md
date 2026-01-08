# Live Domain Context

## Responsibility
Real-time video streaming from cameras to clients.

## Components
- Camera entity (source configuration)
- Stream aggregate (MediaMTX stream state)
- Viewer value object (client connection)

## Boundaries
- Owns: stream start/stop, viewer count, camera online status
- Does not own: recording, playback, detection results

## Key Operations
- Start stream: POST camera config to MediaMTX API
- Stop stream: DELETE from MediaMTX
- Get viewers: Query MediaMTX /v3/paths/{name}

## Events Published
- StreamStarted
- StreamStopped
- CameraOffline
