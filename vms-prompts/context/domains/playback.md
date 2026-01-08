# Playback Domain Context

## Responsibility
Video retrieval and playback from recorded storage.

## Components
- Recording entity (file metadata, duration, camera reference)
- Segment value object (time range within recording)
- PlaybackSession aggregate (client playback state)

## Boundaries
- Owns: recording index, segment retrieval, playback position
- Does not own: live streams, frame extraction, AI results

## Key Operations
- List recordings: Query by camera, time range
- Get segment: Return HLS playlist for time range
- Export clip: Trigger FFmpeg extraction job

## Events Published
- RecordingCompleted
- RecordingDeleted
- ExportReady
