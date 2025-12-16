# Kong API Gateway - GT-Vision

## 🎯 Visão Geral

Kong atua como API Gateway centralizado, fornecendo:
- **Rate Limiting** enterprise-grade
- **CORS** configurado
- **Métricas Prometheus**
- **Request/Correlation IDs** para tracing
- **Roteamento inteligente** para Django e Gateway FastAPI

## 🏗️ Arquitetura

```
HAProxy (porta 80)
    ↓
Kong (porta 8000)
    ↓
    ├─→ /api/*       → Django Backend (porta 8000)
    ├─→ /fast-api/*  → Gateway FastAPI (porta 8000)
    └─→ /admin/*     → Django Admin (porta 8000)
```

## 📊 Modo de Operação

**DB-less Mode (Declarativo):**
- Configuração via arquivo `kong.yml`
- Sem necessidade de PostgreSQL/Cassandra
- Ideal para MVP (simplicidade)
- Reload via `kong reload`

## 🔧 Configurações

### Rate Limiting

| Rota | Limite/min | Limite/hora |
|------|------------|-------------|
| `/api/*` | 100 | 10,000 |
| `/fast-api/*` | 1,000 | 100,000 |
| `/admin/*` | 30 | 500 |

### CORS

- **Django API**: Origens específicas (localhost, frontend)
- **Gateway FastAPI**: Todas origens (bulk ingest)

## 🚀 Uso

### Acessar Kong Manager (GUI)
```bash
http://localhost:8002
```

### Acessar Admin API
```bash
http://localhost:8001
```

### Testar Rotas

**Django API:**
```bash
curl http://localhost:8000/api/cameras/
```

**Gateway FastAPI:**
```bash
curl http://localhost:8000/fast-api/health
```

**Admin:**
```bash
curl http://localhost:8000/admin/login/
```

### Métricas Prometheus
```bash
curl http://localhost:8001/metrics
```

## 📈 Monitoramento

Kong expõe métricas em formato Prometheus:
- Request count
- Latency (p50, p95, p99)
- Bandwidth
- Status codes

## 🔄 Reload de Configuração

Após alterar `kong.yml`:
```bash
docker exec gtvision_kong kong reload
```

## 🎛️ Ajustes de Performance

### Para 250 câmeras + 100 usuários:

**Aumentar rate limits:**
```yaml
plugins:
  - name: rate-limiting
    config:
      minute: 500  # Aumentar conforme necessário
```

**Aumentar timeouts:**
```yaml
services:
  - name: django-api
    connect_timeout: 10000  # 10s
    write_timeout: 120000   # 2min
    read_timeout: 120000    # 2min
```

## 🔐 Segurança (Futuro)

Para produção, adicionar:
- JWT validation plugin (integração com Keycloak)
- IP restriction
- Bot detection
- Request size limiting

## 📝 Logs

Kong logs são enviados para stdout/stderr:
```bash
docker logs gtvision_kong -f
```
