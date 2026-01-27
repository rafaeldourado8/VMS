# Commit - PASSO 5

```bash
git add src/shared/streaming/
git add src/infrastructure/cache/streaming/
git add src/infrastructure/servers/mediamtx/
git add src/infrastructure/test/passo5_streaming/
git add src/docker/streaming/
git add docker-compose.yml
git add docs/passo5-streaming/

git commit -m "feat: StreamingManager com Redis e MediaMTX

PASSO 5 - StreamingManager (core):
- Interface StreamingManager (core)
- RedisStreamingManager (implementação)
- HTTPMediaMTXAdapter (integração)
- FastAPI endpoints (start/stop/list)
- Streaming sob demanda
- Destroy ao fechar
- 5 testes passando

Arquitetura:
- Core: abstrações puras (DDD)
- Infrastructure: implementações (Redis, MediaMTX)
- API: FastAPI em shared/streaming/stream/

Regras:
- Streaming só inicia quando solicitado
- Path removido do MediaMTX ao parar
- Sessão no Redis com TTL 1h
- city_id obrigatório em tudo

Stack:
- FastAPI + Uvicorn
- Redis (sessões)
- MediaMTX (streaming)

Testes: ✅ 5/5 passing

Refs: RULES.md PASSO 5"
```
