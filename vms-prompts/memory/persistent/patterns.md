# Persistent Patterns

## Repository Pattern
```python
class CameraRepository(Protocol):
    def get(self, id: UUID) -> Camera | None: ...
    def save(self, camera: Camera) -> None: ...
    def list(self, filters: CameraFilters) -> list[Camera]: ...
```

## Service Layer Pattern
```python
class StartStreamUseCase:
    def __init__(self, camera_repo, stream_service):
        self.camera_repo = camera_repo
        self.stream_service = stream_service
    
    def execute(self, camera_id: UUID) -> StreamResult:
        camera = self.camera_repo.get(camera_id)
        return self.stream_service.start(camera)
```

## Event Publishing Pattern
```python
class DomainEvent:
    occurred_at: datetime
    aggregate_id: UUID

class EventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None: ...
```

## Error Handling Pattern
Domain exceptions inherit from `DomainError`. Infrastructure exceptions wrap external errors.
