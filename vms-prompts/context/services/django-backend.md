# Django Backend Service Context

## Role
Primary API, business logic, and domain orchestration.

## Project Structure
```
src/
  apps/
    live/          # Live domain
    playback/      # Playback domain
    ai/            # AI domain
    users/         # Authentication
  core/
    domain/        # Shared domain primitives
    infrastructure/# DB, cache, queue adapters
    api/           # REST serializers, views
```

## DDD Layers
- `domain/` - Entities, value objects, domain services
- `application/` - Use cases, command handlers
- `infrastructure/` - Repositories, external adapters
- `api/` - HTTP interface only

## Database Models
Located in `infrastructure/models.py` per app. Domain entities are separate.

## Async Tasks
Celery workers consume from RabbitMQ. Task definitions in `application/tasks.py`.
