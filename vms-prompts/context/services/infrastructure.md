# Infrastructure Context

## Kong API Gateway
- Route: /api/* -> Django
- Route: /stream/* -> Streaming Service
- Route: /ai/* -> AI Service
- Auth: JWT validation on all routes

## HAProxy
- Frontend: ports 80, 443
- Backend pools: django (2 instances), streaming (2 instances)
- Health: GET /health every 5s

## Redis
- Session storage: prefix `session:`
- Cache: prefix `cache:`
- Pub/Sub: stream status notifications

## RabbitMQ
- Exchange: `ai.frames` (topic)
- Exchange: `events` (fanout)
- Queue: `ai.processing`
- Queue: `recording.jobs`

## PostgreSQL
- Database: vms_main
- Schema per domain: live, playback, ai, users
