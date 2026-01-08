# AI Domain Context

## Responsibility
Object detection, face recognition, and analytics on video frames.

## Components
- DetectionRequest entity (frame reference, provider, config)
- DetectionResult aggregate (bounding boxes, labels, confidence)
- AnalyticsEvent value object (triggered rule match)

## Boundaries
- Owns: detection execution, result storage, analytics rules
- Does not own: frame extraction, video streaming, recording

## Key Operations
- Process frame: Receive JPEG from queue, call provider, store result
- Query detections: Filter by camera, time, label
- Configure rules: Define triggers (person detected, vehicle count)

## Events Published
- DetectionCompleted
- AnalyticsTriggered
- ProviderError

## Provider Interface
All providers implement: `detect(frame: bytes, config: dict) -> DetectionResult`
