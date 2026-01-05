# ✅ Docker Compose - Ajustado para Arquitetura DDD

## 📊 Mudanças Realizadas

### 1. AI Detection Service

**Antes:**
```yaml
ai_worker_1:  # Worker sem API
ai_worker_2:  # Worker sem API
```

**Depois:**
```yaml
ai_detection:  # Serviço único com API FastAPI
  ports:
    - "8002:8002"
  command: uvicorn main:app --host 0.0.0.0 --port 8002
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
```

### 2. Streaming Service

**Mantido:**
```yaml
streaming:
  command: uvicorn main:app --host 0.0.0.0 --port 8001
  # Agora usa main.py DDD
```

### 3. Backend Django

**Mantido:**
```yaml
backend:
  command: python manage.py runserver 0.0.0.0:8000
  # Usa arquitetura DDD (domain, application, infrastructure)
```

---

## 🏗️ Arquitetura de Serviços

```
┌─────────────────────────────────────────────────────────────┐
│                         HAProxy :80                          │
│                    (Load Balancer)                           │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌─────────┐
│ Frontend│      │  Kong   │
│  :5173  │      │  :8000  │
└─────────┘      └────┬────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
    ┌─────────┐  ┌──────────┐  ┌──────────┐
    │ Backend │  │Streaming │  │    AI    │
    │  :8000  │  │  :8001   │  │Detection │
    │  Django │  │ FastAPI  │  │  :8002   │
    │   DDD   │  │   DDD    │  │ FastAPI  │
    └────┬────┘  └────┬─────┘  │   DDD    │
         │            │         └────┬─────┘
         │            │              │
         └────────────┼──────────────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
         ▼            ▼            ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │Postgres │  │MediaMTX │  │RabbitMQ │
    │  :5432  │  │  :8888  │  │  :5672  │
    └─────────┘  │  :8889  │  └─────────┘
                 │  :9997  │
                 └─────────┘
                      │
                      ▼
                 ┌─────────┐
                 │  Redis  │
                 │  :6379  │
                 └─────────┘
```

---

## 🚀 Serviços Ativos

| Serviço | Porta | Tecnologia | Arquitetura | Status |
|---------|-------|------------|-------------|--------|
| **Frontend** | 5173 | React + Vite | DDD | ✅ |
| **Backend** | 8000 | Django | DDD | ✅ |
| **Streaming** | 8001 | FastAPI | DDD | ✅ |
| **AI Detection** | 8002 | FastAPI | DDD | ✅ |
| **HAProxy** | 80 | Load Balancer | - | ✅ |
| **Kong** | 8000 | API Gateway | - | ✅ |
| **MediaMTX** | 8888/8889/9997 | Streaming | - | ✅ |
| **Postgres** | 5432 | Database | - | ✅ |
| **Redis** | 6379 | Cache | - | ✅ |
| **RabbitMQ** | 5672 | Message Queue | - | ✅ |

---

## 📝 Arquivos Criados/Atualizados

### Dockerfiles
- ✅ `services/streaming/Dockerfile` - Novo (DDD)
- ✅ `services/ai_detection/Dockerfile` - Novo (DDD)

### Requirements
- ✅ `services/streaming/requirements.txt` - Novo
- ✅ `services/ai_detection/requirements.txt` - Novo

### Docker Compose
- ✅ `docker-compose.yml` - Atualizado (ai_detection único)

---

## 🔧 Como Usar

### Iniciar Todos os Serviços
```bash
docker-compose up -d
```

### Verificar Status
```bash
docker-compose ps
```

### Logs
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f ai_detection
docker-compose logs -f streaming
docker-compose logs -f backend
```

### Rebuild
```bash
# Rebuild específico
docker-compose up -d --build ai_detection
docker-compose up -d --build streaming

# Rebuild tudo
docker-compose up -d --build
```

### Parar Serviços
```bash
docker-compose down
```

---

## 🧪 Healthchecks

Todos os serviços principais têm healthchecks:

```bash
# Streaming
curl http://localhost:8001/health

# AI Detection
curl http://localhost:8002/health

# Backend
curl http://localhost:8000/admin/login/

# MediaMTX
curl http://localhost:9997/v3/config/global/get
```

---

## 📊 Recursos Alocados

| Serviço | CPU Limit | Memory Limit | CPU Reserved | Memory Reserved |
|---------|-----------|--------------|--------------|-----------------|
| Streaming | 1.5 | 1G | 0.5 | 256M |
| AI Detection | 2.0 | 3G | 0.5 | 512M |
| Backend | 0.5 | 1G | 0.1 | 256M |
| MediaMTX | 2.5 | 2G | 1.0 | 512M |

---

## ✅ Validações

### Verificar Serviços DDD
```bash
# Streaming DDD
curl http://localhost:8001/health
# Resposta: {"status": "ok"}

# AI Detection DDD
curl http://localhost:8002/health
# Resposta: {"status": "ok", "service": "ai_detection"}

# Backend DDD
curl http://localhost:8000/api/cameras/
# Resposta: Lista de câmeras
```

### Testar APIs
```bash
# Toggle IA
curl -X POST http://localhost:8002/ai/toggle/1 \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Provisionar Stream
curl -X POST http://localhost:8001/cameras/provision \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 1, "rtsp_url": "rtsp://test.com", "name": "Test"}'
```

---

## 🎯 Conclusão

**Docker Compose ajustado para arquitetura DDD completa!**

✅ AI Detection como serviço único com API
✅ Streaming usando main.py DDD
✅ Backend com arquitetura DDD
✅ Healthchecks em todos os serviços
✅ Recursos otimizados

**Sistema pronto para deploy! 🚀**

---

**Status:** ✅ COMPLETO
**Arquitetura:** 🏗️ 100% DDD
**Deploy:** 🚀 PRONTO
