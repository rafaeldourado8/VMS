# 🚀 VMS v2 - Roadmap 30 Dias

## 📅 Visão Geral

```
Semana 1: Backend Core     ████████░░ 40%
Semana 2: Streaming + IA   ████████░░ 40%
Semana 3: Frontend         ██████░░░░ 30%
Semana 4: Recording + MVP  ██████████ 50%
```

---

## SEMANA 1: Backend Core (Dias 1-7)

### Dia 1: Setup + Domain
```python
domain/
├── entities/
│   ├── camera.py          # Camera, Detection, Recording
│   └── value_objects.py   # CameraId, PlateNumber, Confidence
├── repositories/          # Interfaces
└── events/                # Domain events
```
**Entrega:** Entidades + Value Objects + Tests

---

### Dia 2: Use Cases
```python
application/
├── use_cases/
│   ├── activate_camera.py
│   ├── create_detection.py
│   └── start_recording.py
└── dtos/                  # Request/Response
```
**Entrega:** 5 use cases principais + Tests

---

### Dia 3: PostgreSQL
```python
infrastructure/
└── persistence/
    ├── models.py          # Django models
    ├── repositories.py    # Implementações
    └── migrations/
```
**Entrega:** Repositórios + Migrations + Tests

---

### Dia 4: Redis Cache
```python
infrastructure/
└── cache/
    ├── redis_cache.py
    └── decorators.py      # @cached
```
**Entrega:** Cache layer + Invalidation

---

### Dia 5: API REST
```python
presentation/
└── api/
    ├── cameras/           # ViewSets
    ├── detections/
    └── serializers/
```
**Entrega:** CRUD completo + OpenAPI

---

### Dia 6: Dependency Injection
```python
config/
└── container.py           # DI container
```
**Entrega:** DI + Config + Env vars

---

### Dia 7: Tests + Refactor
- Unit tests: 100%
- Integration tests
- Complexidade < 10
- SOLID check

---

## SEMANA 2: Streaming + IA (Dias 8-14)

### Dia 8: MediaMTX Integration
```python
infrastructure/
└── streaming/
    ├── mediamtx_client.py
    └── stream_service.py
```
**Entrega:** Start/Stop stream + HLS URLs

---

### Dia 9: YOLO Setup
```python
infrastructure/
└── ai/
    ├── yolo_detector.py
    └── models/            # YOLOv8n weights
```
**Entrega:** Detecção de veículos

---

### Dia 10: OCR Integration
```python
infrastructure/
└── ai/
    └── ocr_engine.py      # Fast-Plate-OCR
```
**Entrega:** Leitura de placas

---

### Dia 11: Detection Pipeline
```python
application/
└── services/
    └── detection_pipeline.py
```
**Entrega:** Frame → YOLO → OCR → DB

---

### Dia 12: Celery Tasks
```python
infrastructure/
└── tasks/
    ├── process_frame.py
    └── celery_config.py
```
**Entrega:** Processamento assíncrono

---

### Dia 13: WebSocket
```python
infrastructure/
└── websocket/
    └── consumers.py       # Django Channels
```
**Entrega:** Real-time detections

---

### Dia 14: Tests + Performance
- Load test: 20 câmeras
- Latency < 500ms
- Throughput: 1000 frames/s

---

## SEMANA 3: Frontend (Dias 15-21)

### Dia 15: Setup React
```typescript
src/
├── domain/                # Entities
├── application/           # Use cases
├── infrastructure/        # API, WebSocket
└── presentation/          # Components
```
**Entrega:** Estrutura DDD

---

### Dia 16: Camera Grid
```typescript
components/
├── CameraGrid.tsx
├── CameraCard.tsx
└── VideoPlayer.tsx
```
**Entrega:** Grid 3x3 + Lazy loading

---

### Dia 17: HLS Player
```typescript
components/
└── VideoPlayer.tsx        # HLS.js + cache
```
**Entrega:** Player + Thumbnail (10s)

---

### Dia 18: Detection List
```typescript
components/
├── DetectionList.tsx
├── DetectionFilters.tsx
└── DetectionRow.tsx
```
**Entrega:** Lista + Filtros + Export

---

### Dia 19: Real-time
```typescript
hooks/
└── useRealtimeDetections.ts
```
**Entrega:** WebSocket + Notifications

---

### Dia 20: State Management
```typescript
stores/
├── cameraStore.ts
├── detectionStore.ts
└── authStore.ts
```
**Entrega:** Zustand stores

---

### Dia 21: Tests + Polish
- Component tests
- E2E tests (Playwright)
- Lighthouse > 90

---

## SEMANA 4: Recording + MVP (Dias 22-30)

### Dia 22: Recording Domain
```python
domain/
└── aggregates/
    └── recording.py
```
**Entrega:** Recording entity + logic

---

### Dia 23: FFmpeg Recorder
```python
infrastructure/
└── recording/
    └── ffmpeg_recorder.py
```
**Entrega:** Gravação contínua (1h segments)

---

### Dia 24: Playback API
```python
application/
└── use_cases/
    ├── search_recordings.py
    └── get_segment.py
```
**Entrega:** Busca + Reprodução

---

### Dia 25: Timeline Component
```typescript
components/
└── Timeline.tsx
```
**Entrega:** Timeline interativa

---

### Dia 26: Clip System
```python
application/
└── use_cases/
    └── create_clip.py
```
**Entrega:** Clipes permanentes

---

### Dia 27: Optimization
- Query optimization
- Bundle size < 500KB
- API < 200ms (P95)

---

### Dia 28: Documentation
- API docs (Swagger)
- README
- Architecture (C4)

---

### Dia 29: Security + Monitoring
- JWT auth
- RBAC
- Prometheus + Grafana

---

### Dia 30: Deploy
- Docker Compose
- CI/CD (GitHub Actions)
- Demo video

---

## 🎯 MVP Features

### Core (Obrigatório)
- [x] Streaming HLS (20 câmeras)
- [x] Detecção LPR (YOLO + OCR)
- [x] Lista de detecções
- [x] Gravação contínua (7 dias)
- [x] Playback básico

### Nice-to-Have (Opcional)
- [ ] Timeline avançada
- [ ] Clipes permanentes
- [ ] Busca retroativa
- [ ] Relatórios
- [ ] Multi-tenant

---

## 📊 Métricas de Sucesso

### Performance
```
✓ API Response: < 200ms
✓ Stream Start: < 2s
✓ Detection Latency: < 500ms
✓ Frontend Load: < 3s
```

### Qualidade
```
✓ Test Coverage: > 90%
✓ Cyclomatic Complexity: < 10
✓ SOLID: 100%
✓ Zero Critical Bugs
```

### Escalabilidade
```
✓ 20 câmeras simultâneas
✓ 100 usuários DAU
✓ 1000 detecções/dia
✓ 99.9% uptime
```

---

## 🛠️ Stack Final

### Backend
```
Django 5.1 + DRF
PostgreSQL 15
Redis 7
Celery + RabbitMQ
```

### Frontend
```
React 18 + Vite
TypeScript
Zustand
TailwindCSS
```

### Streaming
```
MediaMTX
FFmpeg
HLS.js
```

### IA
```
YOLOv8n (CPU)
Fast-Plate-OCR
```

### DevOps
```
Docker Compose
Nginx
Prometheus + Grafana
GitHub Actions
```

---

## 📦 Estrutura Final

```
vms-v2/
├── backend/
│   ├── domain/              # Entidades, VOs, Repos
│   ├── application/         # Use Cases, DTOs
│   ├── infrastructure/      # DB, Cache, APIs
│   └── presentation/        # Controllers, Serializers
├── frontend/
│   ├── domain/              # Entities
│   ├── application/         # Use Cases
│   ├── infrastructure/      # API, WebSocket
│   └── presentation/        # Components, Pages
├── services/
│   ├── streaming/           # MediaMTX wrapper
│   └── ai/                  # YOLO + OCR
├── docker-compose.yml
└── docs/
```

---

## 🚦 Checkpoints

### Checkpoint 1 (Dia 7)
- [ ] Backend API funcionando
- [ ] CRUD de câmeras
- [ ] Tests > 90%

### Checkpoint 2 (Dia 14)
- [ ] Streaming HLS
- [ ] Detecção LPR
- [ ] Real-time updates

### Checkpoint 3 (Dia 21)
- [ ] Frontend completo
- [ ] Grid de câmeras
- [ ] Lista de detecções

### Checkpoint 4 (Dia 30)
- [ ] Gravação + Playback
- [ ] Deploy funcionando
- [ ] Demo pronto

---

## 💡 Princípios

1. **YAGNI** - Não implemente o que não precisa
2. **KISS** - Mantenha simples
3. **DRY** - Não repita código
4. **SOLID** - Princípios de design
5. **TDD** - Testes primeiro

---

## 🎬 Próximos Passos

1. **Criar repositório:** `git init vms-v2`
2. **Setup inicial:** Django + React
3. **Dia 1:** Começar domain layer
4. **Daily commits:** Progresso diário
5. **Demo semanal:** Validar progresso

---

**Tempo:** 30 dias × 10h/dia = 300 horas  
**MVP:** Funcional e escalável  
**Qualidade:** Production-ready  
**Deploy:** Docker Compose

🚀 **Comece amanhã!**
