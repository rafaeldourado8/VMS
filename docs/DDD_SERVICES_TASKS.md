# ✅ Tarefas - Expansão DDD para Serviços FastAPI

## 📅 Fase 1: Streaming Service DDD (3-4 dias)

### Setup Inicial
- [ ] Criar estrutura de diretórios domain/application/infrastructure
- [ ] Configurar pytest para streaming service
- [ ] Adicionar radon para análise CC

### Domain Layer - Streaming
- [ ] `domain/streaming/entities/stream.py`
  - [ ] Classe Stream (id, camera_id, path, status, viewers)
  - [ ] Métodos: start(), stop(), is_active()
  - [ ] Testes unitários (5 testes)

- [ ] `domain/streaming/value_objects/stream_path.py`
  - [ ] Validação de path (cam_{id})
  - [ ] Testes unitários (3 testes)

- [ ] `domain/streaming/value_objects/hls_url.py`
  - [ ] Geração de URL HLS
  - [ ] Testes unitários (3 testes)

- [ ] `domain/streaming/repositories/stream_repository.py`
  - [ ] Interface com métodos: save, find_by_camera, delete

### Application Layer - Streaming
- [ ] `application/streaming/commands/provision_stream_command.py`
- [ ] `application/streaming/commands/remove_stream_command.py`
- [ ] `application/streaming/queries/get_stream_status_query.py`
- [ ] `application/streaming/handlers/provision_stream_handler.py`
  - [ ] Testes com mocks (3 testes)
- [ ] `application/streaming/handlers/remove_stream_handler.py`
  - [ ] Testes com mocks (2 testes)

### Infrastructure Layer - Streaming
- [ ] `infrastructure/mediamtx/mediamtx_client.py`
  - [ ] HTTP client para MediaMTX API
  - [ ] Métodos: add_path, remove_path, get_path_status
  - [ ] Testes de integração (4 testes)

- [ ] `infrastructure/repositories/in_memory_stream_repository.py`
  - [ ] Implementação em memória
  - [ ] Testes de integração (3 testes)

### API Layer - Streaming
- [ ] Refatorar `api/routes.py` para usar handlers
- [ ] Manter compatibilidade com endpoints existentes
- [ ] Testes E2E (5 testes)

---

## 📅 Fase 2: AI Detection Service DDD (5-6 dias)

### Setup Inicial
- [ ] Criar estrutura de diretórios domain/application/infrastructure
- [ ] Configurar pytest para ai_detection service
- [ ] Adicionar radon para análise CC

### Domain Layer - AI Detection

#### Entidades
- [ ] `domain/detection/entities/vehicle.py`
  - [ ] Classe Vehicle (id, bbox, track_id, velocity)
  - [ ] Métodos: update_position(), crossed_line()
  - [ ] Testes unitários (6 testes)

- [ ] `domain/detection/entities/roi.py`
  - [ ] Classe ROI (polygon, enabled, camera_id)
  - [ ] Métodos: contains_point(), is_enabled()
  - [ ] Testes unitários (5 testes)

- [ ] `domain/detection/entities/virtual_line.py`
  - [ ] Classe VirtualLine (p1, p2, name)
  - [ ] Métodos: intersects(), distance_to()
  - [ ] Testes unitários (5 testes)

#### Value Objects
- [ ] `domain/detection/value_objects/point.py`
  - [ ] Classe Point (x, y)
  - [ ] Validação de coordenadas
  - [ ] Testes unitários (3 testes)

- [ ] `domain/detection/value_objects/polygon.py`
  - [ ] Classe Polygon (points)
  - [ ] Validação (mínimo 3 pontos)
  - [ ] Testes unitários (4 testes)

- [ ] `domain/detection/value_objects/bounding_box.py`
  - [ ] Classe BoundingBox (x, y, w, h)
  - [ ] Métodos: center(), area()
  - [ ] Testes unitários (4 testes)

#### Services
- [ ] `domain/detection/services/trigger_service.py`
  - [ ] Lógica P1-P2 (ativação OCR)
  - [ ] Cálculo de velocidade
  - [ ] Testes unitários (8 testes, CC < 10)

- [ ] `domain/detection/services/detection_service.py`
  - [ ] Filtro por ROI
  - [ ] Tracking de veículos
  - [ ] Testes unitários (6 testes)

### Application Layer - AI Detection
- [ ] `application/detection/commands/process_frame_command.py`
- [ ] `application/detection/commands/toggle_ai_command.py`
- [ ] `application/detection/commands/update_roi_command.py`
- [ ] `application/detection/queries/get_ai_status_query.py`

- [ ] `application/detection/handlers/process_frame_handler.py`
  - [ ] Orquestração YOLO + OCR + Trigger
  - [ ] Testes com mocks (5 testes)

- [ ] `application/detection/handlers/toggle_ai_handler.py`
  - [ ] Ativar/desativar IA por câmera
  - [ ] Testes com mocks (3 testes)

- [ ] `application/detection/handlers/update_roi_handler.py`
  - [ ] Atualizar ROI e linhas virtuais
  - [ ] Testes com mocks (3 testes)

### Infrastructure Layer - AI Detection
- [ ] `infrastructure/yolo/yolo_detector.py`
  - [ ] Wrapper YOLOv8
  - [ ] Otimização de CPU
  - [ ] Testes de integração (4 testes)

- [ ] `infrastructure/ocr/ocr_engine.py`
  - [ ] Wrapper EasyOCR/Tesseract
  - [ ] Normalização de placas
  - [ ] Testes de integração (4 testes)

- [ ] `infrastructure/messaging/rabbitmq_publisher.py`
  - [ ] Publicar detecções na fila
  - [ ] Testes de integração (3 testes)

- [ ] `infrastructure/repositories/camera_config_repository.py`
  - [ ] Carregar ROI e linhas por câmera
  - [ ] Cache Redis
  - [ ] Testes de integração (3 testes)

### API Layer - AI Detection
- [ ] POST `/ai/toggle/{camera_id}` (ativar/desativar)
- [ ] POST `/ai/roi/{camera_id}` (atualizar ROI)
- [ ] GET `/ai/status/{camera_id}` (status IA)
- [ ] Testes E2E (6 testes)

---

## 📅 Fase 3: Frontend Refactoring (4-5 dias)

### Domain Layer (TypeScript)
- [ ] `src/domain/entities/Camera.ts`
- [ ] `src/domain/entities/Detection.ts`
- [ ] `src/domain/entities/ROI.ts`
- [ ] `src/domain/value-objects/Point.ts`
- [ ] `src/domain/value-objects/Polygon.ts`

### Application Layer
- [ ] `src/application/use-cases/CreateCameraUseCase.ts`
- [ ] `src/application/use-cases/ToggleAIUseCase.ts`
- [ ] `src/application/use-cases/DrawROIUseCase.ts`
- [ ] `src/application/use-cases/ListDetectionsUseCase.ts`

### Infrastructure Layer
- [ ] `src/infrastructure/api/CameraApiClient.ts`
- [ ] `src/infrastructure/api/DetectionApiClient.ts`
- [ ] `src/infrastructure/api/AIApiClient.ts`
- [ ] `src/infrastructure/websocket/EventsWebSocket.ts`

### Presentation Layer
- [ ] Refatorar `CamerasPage.tsx` para usar use cases
- [ ] Refatorar `DetectionsPage.tsx`
- [ ] Criar `ROIDrawer.tsx` (canvas para desenho)
- [ ] Criar `AIToggle.tsx` (botão ativar/desativar)
- [ ] Testes de componentes (10 testes)

---

## 📊 Métricas de Sucesso

### Streaming Service
- [ ] Testes: > 40
- [ ] CC: < 5
- [ ] Cobertura: > 80%
- [ ] Latência: < 2s

### AI Detection Service
- [ ] Testes: > 60
- [ ] CC: < 10
- [ ] Cobertura: > 80%
- [ ] CPU: < 1% por câmera

### Frontend
- [ ] Testes: > 30
- [ ] CC: < 10
- [ ] Cobertura: > 70%
- [ ] Performance: FPS > 60

---

## 🎯 Entregáveis Finais

- [ ] Streaming service refatorado com DDD
- [ ] AI detection service refatorado com DDD
- [ ] Frontend refatorado com arquitetura limpa
- [ ] Suite de testes completa (> 130 testes)
- [ ] Documentação atualizada
- [ ] Scripts de análise de qualidade
- [ ] ROI e linhas virtuais funcionando
- [ ] Toggle IA por câmera funcionando
- [ ] Performance mantida/melhorada

---

**Tempo estimado total**: 12-15 dias úteis

**Status**: Aguardando aprovação para iniciar Fase 1
