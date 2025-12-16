# 🚀 Kong API Gateway - Quick Start

## 📋 O que foi implementado

Kong API Gateway agora está integrado ao GT-Vision como camada centralizada de API management.

### Arquitetura Atualizada

```
Cliente
  ↓
HAProxy (porta 80)
  ↓
Kong API Gateway (porta 8000)
  ↓
  ├─→ /api/*       → Django Backend
  ├─→ /fast-api/*  → Gateway FastAPI
  └─→ /admin/*     → Django Admin
```

## 🎯 Funcionalidades Ativas

✅ **Rate Limiting**
- `/api/*`: 100 req/min, 10k req/hora
- `/fast-api/*`: 1000 req/min, 100k req/hora
- `/admin/*`: 30 req/min, 500 req/hora

✅ **CORS** configurado para frontend

✅ **Métricas Prometheus** em `/metrics`

✅ **Request/Correlation IDs** para tracing

✅ **DB-less mode** (sem PostgreSQL extra)

## 🚀 Como Usar

### 1. Iniciar o sistema

```bash
docker-compose up -d
```

### 2. Verificar Kong

```bash
# Health check
curl http://localhost:8000/

# Admin API
curl http://localhost:8001/

# Kong Manager GUI
open http://localhost:8002
```

### 3. Testar rotas

```bash
# Django API via Kong
curl http://localhost:8000/api/cameras/

# Gateway FastAPI via Kong
curl http://localhost:8000/fast-api/health

# Django Admin via Kong
curl http://localhost:8000/admin/login/
```

### 4. Rodar testes automatizados

```bash
bash test_kong.sh
```

## 📊 Monitoramento

### Métricas Prometheus

```bash
curl http://localhost:8001/metrics
```

Métricas disponíveis:
- `kong_http_requests_total` - Total de requests
- `kong_latency_ms` - Latência (p50, p95, p99)
- `kong_bandwidth_bytes` - Bandwidth
- `kong_http_status` - Status codes

### Kong Manager GUI

Acesse: http://localhost:8002

Interface gráfica para:
- Visualizar rotas
- Monitorar tráfego
- Gerenciar plugins
- Ver logs

## 🔧 Configuração

### Arquivo: `kong/kong.yml`

Configuração declarativa do Kong. Para modificar:

1. Edite `kong/kong.yml`
2. Valide: `docker exec gtvision_kong kong config parse /etc/kong/kong.yml`
3. Reload: `docker exec gtvision_kong kong reload`

### Adicionar nova rota

```yaml
services:
  - name: meu-servico
    url: http://meu-backend:8000
    routes:
      - name: minha-rota
        paths:
          - /minha-api
    plugins:
      - name: rate-limiting
        config:
          minute: 100
```

### Ajustar rate limits

```yaml
plugins:
  - name: rate-limiting
    config:
      minute: 500    # Aumentar limite
      hour: 50000
      policy: local  # ou 'redis' para cluster
```

## 🔐 Próximos Passos (Keycloak)

Após implementar Keycloak, adicionar JWT validation:

```yaml
plugins:
  - name: jwt
    config:
      key_claim_name: kid
      secret_is_base64: false
      claims_to_verify:
        - exp
```

## 🐛 Troubleshooting

### Kong não inicia

```bash
# Ver logs
docker logs gtvision_kong

# Validar config
docker exec gtvision_kong kong config parse /etc/kong/kong.yml
```

### Rate limit não funciona

```bash
# Verificar se plugin está ativo
curl http://localhost:8001/plugins

# Testar com múltiplas requests
for i in {1..150}; do curl http://localhost:8000/api/cameras/; done
```

### Rotas não funcionam

```bash
# Listar rotas configuradas
curl http://localhost:8001/routes

# Verificar serviços
curl http://localhost:8001/services
```

## 📈 Performance

### Para 250 câmeras + 100 usuários:

**Recursos Kong:**
- CPU: 1-2 cores
- RAM: 512MB-1GB
- Latência adicional: ~5-10ms

**Otimizações:**
- Usar `policy: redis` para rate limiting distribuído
- Adicionar múltiplas instâncias Kong (HA)
- Configurar cache plugin para endpoints pesados

## 📚 Documentação

- Kong Docs: https://docs.konghq.com/
- Plugins: https://docs.konghq.com/hub/
- DB-less mode: https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/

## ✅ Checklist de Validação

- [ ] Kong rodando (porta 8000)
- [ ] Admin API acessível (porta 8001)
- [ ] Kong Manager GUI acessível (porta 8002)
- [ ] Rotas Django funcionando via Kong
- [ ] Rotas Gateway FastAPI funcionando via Kong
- [ ] Rate limiting ativo (429 após limite)
- [ ] CORS funcionando
- [ ] Métricas Prometheus disponíveis
- [ ] HAProxy roteando para Kong
- [ ] Health checks passando

## 🎉 Pronto!

Kong está configurado e pronto para uso. Próximo passo: **Keycloak** para autenticação centralizada.
