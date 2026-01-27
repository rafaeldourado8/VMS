# PASSO 5 - StreamingManager (Core)

## Objetivo

Orquestrar streaming sob demanda com isolamento multi-tenant.

## Arquitetura

```
shared/streaming/core/          # Abstrações (DDD)
├── streaming_manager.py        # Interface
└── models.py                   # StreamingSession

infrastructure/cache/streaming/ # Implementação Redis
└── redis_streaming_manager.py

infrastructure/servers/mediamtx/ # Adapter MediaMTX
├── adapter.py                   # Interface
└── http_adapter.py              # HTTP client

shared/streaming/stream/         # API FastAPI
└── api.py
```

## Fluxo

1. **Start**: `POST /api/streaming/start/{camera_public_id}`
   - Valida câmera (city_id)
   - Adiciona path no MediaMTX
   - Salva sessão no Redis (TTL 1h)
   - Retorna `session_id` + `hls_url`

2. **Stop**: `POST /api/streaming/stop/{session_id}`
   - Remove path do MediaMTX
   - Deleta sessão do Redis

3. **List**: `GET /api/streaming/sessions`
   - Lista sessões ativas da cidade

## Regras

- **Streaming sob demanda**: Só inicia quando usuário solicita
- **Destroy ao fechar**: Remove path do MediaMTX
- **Isolamento**: city_id obrigatório em tudo
- **TTL**: Sessão expira em 1 hora

## Testes

✅ 5 testes passando

```bash
docker exec -it vms_django python manage.py test infrastructure.test.passo5_streaming
```

## API

**Start Stream:**
```bash
curl -X POST http://localhost:8001/api/streaming/start/{camera_public_id} \
  -H "X-City-ID: {city_uuid}" \
  -H "X-User-ID: 1"
```

**Stop Stream:**
```bash
curl -X POST http://localhost:8001/api/streaming/stop/{session_id} \
  -H "X-City-ID: {city_uuid}"
```

**List Sessions:**
```bash
curl http://localhost:8001/api/streaming/sessions \
  -H "X-City-ID: {city_uuid}"
```

## Próximo passo

**PASSO 6**: Mosaicos (4 streams simultâneos)
