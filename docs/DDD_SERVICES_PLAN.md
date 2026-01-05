# 🚀 Plano de Expansão DDD - Serviços FastAPI

## 🎯 Objetivo

Aplicar DDD nos serviços FastAPI (Streaming e AI Detection), mantendo qualidade, implementando testes e integrando com frontend.

---

## 📋 Escopo

### 1. Serviço de Streaming (FastAPI)
- Refatorar para DDD
- Manter qualidade de streaming
- Testes unitários e integração
- HLS/WebRTC otimizado

### 2. Serviço de AI Detection (FastAPI)
- Refatorar para DDD
- ROI e linhas virtuais (trigger P1-P2)
- Ativar/desativar IA por câmera
- Testes de detecção
- Otimização de CPU

### 3. Frontend (React)
- Refatorar para nova arquitetura
- Integração com handlers DDD
- Desenho de ROI e linhas
- Controle de IA

---

## 🏗️ Arquitetura Proposta

```
services/
├── streaming/                    # Serviço FastAPI
│   ├── domain/                   # Domain Layer
│   │   ├── streaming/
│   │   │   ├── entities/         # Stream, StreamSession
│   │   │   ├── value_objects/    # StreamPath, HLSUrl
│   │   │   └── repositories/     # StreamRepository (interface)
│   │   └── shared/
│   ├── application/              # Application Layer
│   │   ├── commands/             # ProvisionStreamCommand
│   │   ├── queries/              # GetStreamStatusQuery
│   │   └── handlers/             # CQRS handlers
│   ├── infrastructure/           # Infrastructure Layer
│   │   ├── mediamtx/             # MediaMTX client
│   │   └── repositories/         # In-memory repository
│   ├── api/                      # FastAPI routes
│   └── tests/                    # Testes
│
├── ai_detection/                 # Serviço FastAPI
│   ├── domain/                   # Domain Layer
│   │   ├── detection/
│   │   │   ├── entities/         # AIDetection, Vehicle, ROI
│   │   │   ├── value_objects/    # Point, Line, Polygon
│   │   │   └── services/         # DetectionService, TriggerService
│   │   └── shared/
│   ├── application/              # Application Layer
│   │   ├── commands/             # ProcessFrameCommand, ToggleAICommand
│   │   ├── queries/              # GetAIStatusQuery
│   │   └── handlers/             # CQRS handlers
│   ├── infrastructure/           # Infrastructure Layer
│   │   ├── yolo/                 # YOLOv8 wrapper
│   │   ├── ocr/                  # OCR engine
│   │   └── messaging/            # RabbitMQ
│   ├── api/                      # FastAPI routes
│   └── tests/                    # Testes
│
frontend/
├── src/
│   ├── domain/                   # Domain models (TypeScript)
│   ├── application/              # Use cases
│   ├── infrastructure/           # API clients
│   └── presentation/             # Components React
```

---

## 📅 Fases de Implementação

### **Fase 1: Streaming Service DDD** (3-4 dias)

#### Domain Layer
- [ ] Entidade Stream (id, camera_id, path, status)
- [ ] Value Objects (StreamPath, HLSUrl)
- [ ] Interface StreamRepository
- [ ] Testes unitários

#### Application Layer
- [ ] ProvisionStreamCommand
- [ ] RemoveStreamCommand
- [ ] GetStreamStatusQuery
- [ ] Handlers
- [ ] Testes com mocks

#### Infrastructure Layer
- [ ] MediaMTX client (HTTP API)
- [ ] In-memory StreamRepository
- [ ] Testes de integração

#### API Layer
- [ ] Refatorar routes para usar handlers
- [ ] Manter compatibilidade
- [ ] Testes E2E

---

### **Fase 2: AI Detection Service DDD** (5-6 dias)

#### Domain Layer
- [ ] Entidade Vehicle (id, bbox, track_id)
- [ ] Entidade ROI (polygon, enabled)
- [ ] Value Objects (Point, Line, Polygon)
- [ ] Service TriggerService (P1-P2 logic)
- [ ] Service DetectionService
- [ ] Testes unitários (CC < 10)

#### Application Layer
- [ ] ProcessFrameCommand
- [ ] ToggleAICommand (ativar/desativar por câmera)
- [ ] UpdateROICommand
- [ ] GetAIStatusQuery
- [ ] Handlers
- [ ] Testes com mocks

#### Infrastructure Layer
- [ ] YOLOv8 wrapper
- [ ] OCR wrapper (EasyOCR/Tesseract)
- [ ] RabbitMQ publisher
- [ ] Camera config repository
- [ ] Testes de integração

#### API Layer
- [ ] POST /ai/toggle/{camera_id}
- [ ] POST /ai/roi/{camera_id}
- [ ] GET /ai/status/{camera_id}
- [ ] Testes E2E

---

### **Fase 3: Frontend Refactoring** (4-5 dias)

#### Domain Layer (TypeScript)
- [ ] Interfaces Camera, Detection, ROI
- [ ] Value Objects

#### Application Layer
- [ ] Use cases (CreateCamera, ToggleAI, DrawROI)
- [ ] API clients

#### Infrastructure Layer
- [ ] HTTP clients (axios)
- [ ] WebSocket client (eventos)

#### Presentation Layer
- [ ] Refatorar components
- [ ] Canvas para desenho de ROI
- [ ] Toggle IA por câmera
- [ ] Testes (Jest/Vitest)

---

## 🎯 Requisitos Técnicos

### Streaming Service
- **Performance**: Latência < 2s
- **Qualidade**: Sem perda de frames
- **Escalabilidade**: Até 12 câmeras simultâneas
- **Testes**: Cobertura > 80%

### AI Detection Service
- **CPU**: Manter < 1% por câmera (modo econômico)
- **Precisão**: Confidence > 0.8 para placas
- **ROI**: Validação de polígonos
- **Trigger P1-P2**: Lógica de velocidade
- **Testes**: Cobertura > 80%, CC < 10

### Frontend
- **Performance**: Renderização < 16ms
- **UX**: Desenho de ROI intuitivo
- **Responsividade**: Mobile-friendly
- **Testes**: Componentes críticos

---

## 📊 Métricas de Sucesso

| Serviço | Testes | CC | Cobertura | Performance |
|---------|--------|----|-----------| ------------|
| **Streaming** | > 40 | < 5 | > 80% | Latência < 2s |
| **AI Detection** | > 60 | < 10 | > 80% | CPU < 1% |
| **Frontend** | > 30 | < 10 | > 70% | FPS > 60 |

---

## 🚀 Próximos Passos

1. **Aprovação do plano**
2. **Fase 1: Streaming Service DDD**
3. **Fase 2: AI Detection Service DDD**
4. **Fase 3: Frontend Refactoring**
5. **Integração e testes E2E**

---

## 📝 Notas Importantes

- **Backward compatibility**: Manter APIs existentes funcionando
- **Migração gradual**: Implementar novo código ao lado do antigo
- **Feature flags**: Permitir toggle entre implementações
- **Documentação**: Atualizar docs conforme refatoração
- **Performance**: Monitorar CPU e latência durante refatoração

---

**Tempo estimado total**: 12-15 dias úteis

**Prioridade**: Manter sistema funcionando durante refatoração
