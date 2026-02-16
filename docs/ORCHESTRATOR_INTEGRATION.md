# Recording Orchestrator - Guia de Integração

## Visão Geral

O **Recording Orchestrator** é o serviço central que coordena todos os componentes do sistema de gravação.

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│              RECORDING ORCHESTRATOR (Port 8010)              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Event Bus  │  │   Health    │  │   Cleanup   │         │
│  │ Redis Pub/Sub│  │   Monitor   │  │ Coordinator │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    STORAGE      │  │    TIMELINE     │  │     DJANGO      │
│   (Port 8003)   │  │   (Port 8007)   │  │   (Port 8000)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Endpoints

### Health & Monitoring

#### `GET /health`
Status do orquestrador
```json
{"status": "ok", "service": "orchestrator"}
```

#### `GET /services/health`
Status de todos os serviços
```json
{
  "services": [
    {"service": "storage", "status": "healthy", "latency_ms": 12.5},
    {"service": "timeline", "status": "healthy", "latency_ms": 8.3}
  ]
}
```

### Event Bus

#### `POST /events/publish`
Publica evento manualmente
```json
{
  "event_type": "recording.created",
  "camera_id": 1,
  "file_path": "/recordings/camera_1/2026-02-13/10-00-00.mp4",
  "timestamp": "2026-02-13T10:00:00Z",
  "metadata": {}
}
```

**Tipos de eventos:**
- `recording.created` - Nova gravação criada
- `recording.deleted` - Gravação deletada
- `recording.indexed` - Gravação indexada no Storage

### Timeline Proxy

#### `GET /timeline/{camera_id}`
Retorna timeline completa da câmera
```json
{
  "camera_id": 1,
  "blocks": [...],
  "total_duration": 3600,
  "coverage_percent": 98.5
}
```

#### `GET /timeline/{camera_id}/blocks`
Retorna apenas blocos de gravação
```json
{
  "blocks": [
    {
      "start_time": "2026-02-13T10:00:00Z",
      "end_time": "2026-02-13T10:05:00Z",
      "duration": 300,
      "file_size": 15728640,
      "has_gaps": false
    }
  ]
}
```

### Cleanup

#### `POST /cleanup/{camera_id}?retention_days=30`
Orquestra cleanup completo de uma câmera
```json
{
  "camera_id": 1,
  "deleted_count": 150,
  "deleted_files": ["file1.mp4", "file2.mp4", "..."],
  "errors": [],
  "success": true
}
```

#### `POST /timeline/{camera_id}/reindex`
Força reindexação da timeline
```json
{
  "status": "reindexed",
  "camera_id": 1
}
```

### Webhooks

#### `POST /recording/created`
Notifica criação de nova gravação
```json
{
  "camera_id": 1,
  "file_path": "/recordings/camera_1/2026-02-13/10-00-00.mp4"
}
```

## Fluxo de Eventos

### 1. Nova Gravação Criada

```
RECORDER → cria arquivo → POST /recording/created
                              ↓
                    Orchestrator publica evento
                              ↓
                    ┌─────────┴─────────┐
                    ▼                   ▼
              STORAGE scan         TIMELINE reindex
```

### 2. Cleanup de Gravações

```
CRON/Manual → POST /cleanup/{camera_id}
                    ↓
          Orchestrator coordena:
                    ↓
          1. Deleta arquivos
          2. Publica eventos
          3. Reindex Timeline
          4. Notifica Django
```

### 3. Query de Timeline

```
Frontend → Orchestrator → Timeline Service
              ↓
        Cache hit/miss
              ↓
        Return blocks
```

## Integração com Serviços

### RECORDER
Deve notificar o Orchestrator quando criar novo arquivo:
```python
async def on_segment_created(camera_id, file_path):
    await httpx.post(
        "http://orchestrator:8010/recording/created",
        json={"camera_id": camera_id, "file_path": file_path}
    )
```

### STORAGE
Subscreve eventos via Redis:
```python
pubsub = redis.pubsub()
await pubsub.subscribe("recording_events")
```

### TIMELINE
Recebe comandos de reindexação:
```python
@app.post("/reindex/{camera_id}")
async def reindex(camera_id: int):
    await invalidate_cache(camera_id)
    return await build_timeline(camera_id)
```

### DJANGO
Recebe notificações de cleanup:
```python
@api_view(['POST'])
def cleanup_notification(request):
    camera_id = request.data['camera_id']
    deleted_count = request.data['deleted_count']
    # Atualiza estatísticas
```

## Configuração Docker

Adicionar ao `docker-compose.yml`:

```yaml
orchestrator:
  build:
    context: ./services/orchestrator
    dockerfile: Dockerfile
  container_name: gtvision_orchestrator
  command: uvicorn main:app --host 0.0.0.0 --port 8010
  ports:
    - "8010:8010"
  environment:
    REDIS_URL: redis://redis_cache:6379/4
  depends_on:
    redis_cache:
      condition: service_healthy
    storage:
      condition: service_healthy
    timeline:
      condition: service_healthy
  networks:
    - gtvision_network
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8010/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

## Monitoramento

### Logs
```bash
docker logs -f gtvision_orchestrator
```

### Métricas
```bash
curl http://localhost:8010/services/health
```

### Redis Events
```bash
docker exec -it gtvision_redis redis-cli
> SUBSCRIBE recording_events
```

## Testes

### Publicar evento manualmente
```bash
curl -X POST http://localhost:8010/events/publish \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "recording.created",
    "camera_id": 1,
    "file_path": "/recordings/camera_1/2026-02-13/10-00-00.mp4",
    "timestamp": "2026-02-13T10:00:00Z"
  }'
```

### Testar cleanup
```bash
curl -X POST http://localhost:8010/cleanup/1?retention_days=7
```

### Verificar timeline
```bash
curl http://localhost:8010/timeline/1/blocks
```

## Próximos Passos

1. ✅ Orquestrador criado
2. 🔨 Integrar RECORDER para notificar eventos
3. 🔨 Integrar STORAGE para subscrever eventos
4. 🔨 Criar componente React de Timeline Player
5. 🔨 Implementar barra de progresso com gaps
