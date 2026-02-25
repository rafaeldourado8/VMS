# Quick Fix: Streaming HLS após Restart

## Problema Resolvido ✅
Câmeras não aparecem após restart do backend (erro 404 no HLS)

## Solução Implementada

### 4 Camadas de Proteção:

```
┌─────────────────────────────────────────────────┐
│  1. REDIS PERSISTENCE                           │
│  └─> Salva estado de todas as câmeras          │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  2. STARTUP PROVISIONING                        │
│  └─> Backend reprovisiona ao iniciar           │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  3. AUTO-PROVISION ON ACCESS                    │
│  └─> Provisiona quando frontend acessa         │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  4. HEALTH CHECK (60s)                          │
│  └─> Corrige inconsistências automaticamente   │
└─────────────────────────────────────────────────┘
```

## Como Testar

### Teste Rápido:
```bash
tests\test_backend_restart.bat
```

### Teste Manual:
```bash
# 1. Restart backend
docker restart gtvision_backend

# 2. Aguardar 90s

# 3. Testar acesso
curl http://localhost/hls/cam_15/index.m3u8
```

## Arquivos Modificados

- `services/streaming/main.py` - Redis persistence + auto-provision
- `backend/provision_cameras_startup.py` - Startup provisioning
- `services/streaming/stream_health_check.py` - Health check
- `docker-compose.yml` - Configuração dos serviços

## Logs para Monitorar

```bash
# Backend startup
docker logs gtvision_backend | grep "Provisionando"

# Streaming service
docker logs -f gtvision_streaming | grep "cam_"

# Health check
docker logs -f gtvision_stream_health
```

## Tempo de Recuperação

- **Backend restart:** ~30 segundos
- **MediaMTX crash:** ~30 segundos  
- **Acesso direto (404):** ~2 segundos
- **Health check:** ~60 segundos (máximo)

## Troubleshooting

### Câmera ainda não aparece?

1. Verificar Redis:
```bash
docker exec -it gtvision_redis redis-cli
> KEYS camera:*
> HGETALL camera:15
```

2. Forçar reprovisionamento:
```bash
curl -X POST http://localhost/api/cameras/sync_with_streaming/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. Verificar logs:
```bash
docker logs gtvision_backend --tail 50
docker logs gtvision_streaming --tail 50
```

## Deploy

Para aplicar as mudanças:

```bash
# Rebuild backend
docker-compose build backend

# Rebuild streaming
docker-compose build streaming

# Restart serviços
docker-compose up -d backend streaming stream_health
```

## Rollback

Se houver problemas, remover linha do docker-compose.yml:

```yaml
# ANTES (com fix)
command: sh -c "python provision_cameras_startup.py && python manage.py runserver 0.0.0.0:8000"

# DEPOIS (rollback)
command: sh -c "python manage.py runserver 0.0.0.0:8000"
```
