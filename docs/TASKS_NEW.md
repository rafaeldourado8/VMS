# VMS Implementation Tasks - ARQUITETURA ATUALIZADA

**Status**: Streaming ✅ | LPR Detection ✅ | Recording 🔄 | Sentinela ❌ | Planos ❌

---

## 🎯 VISÃO GERAL DO PROJETO

### Regras de Negócio

#### Câmeras
- **RTSP (LPR)**: 10-20 por cidade - Alta definição - IA LPR ativa
- **RTMP (Bullets)**: até 1000 por cidade - Sem IA - Apenas gravação
- **Gravação**: SEMPRE ativa, independente de visualização

#### Planos de Armazenamento (Cíclico)
```
SuperAdmin 7 dias  → 3 usuários comuns  → Armazenamento cíclico 7 dias
SuperAdmin 15 dias → 5 usuários comuns  → Armazenamento cíclico 15 dias  
SuperAdmin 30 dias → 10 usuários comuns → Armazenamento cíclico 30 dias + diferencial
```

#### Visualização
- **Lista**: Padrão (não grid)
- **Player Individual**: Clique → abre player único
- **Mosaicos**: Ilimitados, mas 4 câmeras/mosaico

#### Sentinela (Busca Retroativa)
- Processa gravações (NÃO tempo real)
- Busca: veículos (cor, tipo, marca) + placas (OCR)
- Uso: Investigação pós-evento

---

## 📦 COMPONENTES DO SISTEMA

### 1. Streaming (MediaMTX) ✅
- HLS/WebRTC para visualização
- Gravação contínua em background
- Independente de viewers

### 2. LPR Detection (YOLO + OCR) ✅
- Processa apenas câmeras RTSP
- YOLO detecta placas
- Fast-Plate-OCR reconhece texto
- Auto-treinamento

### 3. Recording Service 🔄
- Gerencia gravação cíclica
- Planos: 7/15/30 dias
- Clipes permanentes
- Timeline navegável

### 4. Sentinela (YOLO Search) ❌
- Busca retroativa em gravações
- Detecção de veículos
- Filtros: cor, tipo, marca, placa

### 5. Backend (Django) ✅
- API REST
- Gerenciamento de câmeras
- Usuários e planos
- Gravações e clipes

### 6. Frontend (React) ✅
- Lista de câmeras
- Player individual
- Mosaicos (4 câmeras)
- Timeline de gravações
- Busca Sentinela

---

## 📦 PHASE 0: MIGRATION & CLEANUP (1 day)

### Task 0.1: Migrate LEGACY to New Structure
- [ ] Create `services/lpr_detection/` (baseado no LEGACY)
  - Manter YOLO + Fast-Plate-OCR
  - Remover processamento RTSP tempo real
  - Adaptar para processar arquivos de vídeo
- [ ] Create `services/sentinela/` (novo serviço)
  - Busca retroativa em gravações
  - API de consulta por filtros
- [ ] Update `services/ai_detection/` 
  - Renomear para `services/rekognition/` (opcional)
  - Manter apenas se necessário

### Task 0.2: Remove Unused Features
- [ ] Remove WebRTC failover (simplificar para HLS apenas)
- [ ] Remove stream concurrency limits (não faz sentido com lista)
- [ ] Remove snapshot worker (não usado)
- [ ] Clean TASKS.md Phase 1 completed items

---

## 🎥 PHASE 1: RECORDING SERVICE (3-4 days)

### Task 1.1: Storage Service Core
- [ ] Create `services/recording/main.py`
  - FastAPI service
  - Endpoints: `/start`, `/stop`, `/status`
- [ ] Create `services/recording/storage_manager.py`
  - Gravação cíclica (7/15/30 dias)
  - Lógica: `if len(dias) >= plano: sobrescrever dia[0]`
  - Integração com MediaMTX recordings
- [ ] Create `services/recording/models.py`
  - Recording: camera_id, start_time, end_time, file_path, plan
  - Clip: camera_id, start_time, end_time, file_path, permanent=True
- [ ] Add to `docker-compose.yml`
  - Service: recording
  - Volume: recordings_storage

### Task 1.2: MediaMTX Recording Integration
- [ ] Edit `mediamtx.yml`
  - Enable recording for all paths
  - Format: `recordings/{camera_id}/{date}/{time}.mp4`
  - Segment duration: 1 hour
- [ ] Create `services/recording/mediamtx_monitor.py`
  - Monitor MediaMTX recordings folder
  - Update database with new recordings
  - Trigger cleanup when plan expires

### Task 1.3: Plan Management
- [ ] Edit `backend/apps/usuarios/models.py`
  - Add: `storage_plan` (7, 15, 30)
  - Add: `max_users` (3, 5, 10)
- [ ] Create `backend/apps/recordings/models.py`
  - StoragePlan: days, max_users, features
  - Recording: camera, start, end, file_path, plan
  - Clip: recording, start, end, permanent
- [ ] Create `backend/apps/recordings/views.py`
  - GET /recordings/?camera_id=X&date=Y
  - POST /clips/ (create permanent clip)
  - DELETE /recordings/{id} (manual delete)

### Task 1.4: Cyclic Storage Logic
- [ ] Create `services/recording/cyclic_cleaner.py`
  - Cron job: daily at 00:00
  - Check recordings older than plan days
  - Delete files (except clips)
  - Update database
- [ ] Create tests
  - Test 7-day cycle
  - Test clip preservation
  - Test storage calculation

**Acceptance**: Gravação contínua, planos funcionando, clipes permanentes

---

## 🎬 PHASE 2: PLAYBACK & TIMELINE (2-3 days)

### Task 2.1: Playback API
- [ ] Create `backend/apps/recordings/playback.py`
  - GET /playback/{camera_id}?date=YYYY-MM-DD
  - Return: list of recording segments
  - Support: HLS streaming of recordings
- [ ] Create `services/recording/hls_generator.py`
  - Convert MP4 recordings to HLS on-demand
  - Cache HLS playlists (TTL: 1 hour)

### Task 2.2: Timeline Component
- [ ] Create `frontend/src/components/recordings/Timeline.tsx`
  - Date picker
  - Hour bar (00:00 - 23:59)
  - Recording segments visualization
  - Clip markers
  - Seek functionality
- [ ] Create `frontend/src/components/recordings/PlaybackPlayer.tsx`
  - HLS player for recordings
  - Timeline integration
  - Clip creation UI

### Task 2.3: Clip Management
- [ ] Create `frontend/src/pages/ClipsPage.tsx`
  - List all permanent clips
  - Preview thumbnails
  - Download/share
  - Delete
- [ ] Create `backend/apps/recordings/clip_generator.py`
  - Extract clip from recording
  - Generate thumbnail
  - Store permanently

**Acceptance**: Timeline navegável, playback funcional, clipes criados

---

## 🤖 PHASE 3: LPR DETECTION (YOLO + OCR) (2-3 days)

### Task 3.1: Migrate LEGACY Detection
- [ ] Create `services/lpr_detection/` structure
  ```
  lpr_detection/
  ├── main.py (FastAPI)
  ├── detector.py (YOLO + Fast-Plate-OCR)
  ├── models.py (Detection results)
  ├── requirements.txt
  └── Dockerfile
  ```
- [ ] Copy from LEGACY:
  - `detection.py` → `detector.py`
  - `fast-plate-ocr-master/` → keep
  - `yolov8n.pt` → keep
- [ ] Adapt `detector.py`:
  - Remove RTSP processing
  - Add: `process_video_file(video_path, camera_id)`
  - Add: `process_frame_batch(frames, camera_id)`

### Task 3.2: LPR Processing Pipeline
- [ ] Create `services/lpr_detection/processor.py`
  - Input: recording file path
  - Process: 1 frame/second (não tempo real)
  - Output: detections to database
- [ ] Create `services/lpr_detection/models.py`
  - LPRDetection: camera_id, timestamp, plate, confidence, image_path
- [ ] Create API endpoints:
  - POST /process-recording (trigger LPR on recording)
  - GET /detections/?camera_id=X&date=Y

### Task 3.3: Auto-Training Pipeline
- [ ] Keep LEGACY auto-training logic
- [ ] Create `services/lpr_detection/training/`
  - `prepare_dataset.py` (from LEGACY)
  - `retrain.py` (Google Colab integration)
- [ ] Create training trigger:
  - Manual: POST /train
  - Auto: when 1000+ new samples

### Task 3.4: LPR Camera Integration
- [ ] Edit `backend/apps/cameras/models.py`
  - Add: `camera_type` (bullet, lpr)
  - Add: `lpr_enabled` (boolean)
- [ ] Create limit check:
  - Max 20 LPR cameras per tenant
- [ ] Auto-trigger LPR processing on new recordings

**Acceptance**: LPR detecta placas em gravações, auto-treino funciona

---

## 🔍 PHASE 4: SENTINELA (Busca Retroativa) (3-4 days)

### Task 4.1: Sentinela Service Core
- [ ] Create `services/sentinela/main.py`
  - FastAPI service
  - Endpoints: `/search`, `/status/{job_id}`
- [ ] Create `services/sentinela/detector.py`
  - YOLO for vehicle detection
  - Attributes: color, type, brand
  - Process recordings frame-by-frame

### Task 4.2: Search Engine
- [ ] Create `services/sentinela/search.py`
  - Input: camera_ids, date_range, filters (color, type, plate)
  - Process: scan recordings matching criteria
  - Output: list of matches with timestamps
- [ ] Create `services/sentinela/models.py`
  - SearchJob: id, status, progress, results
  - VehicleDetection: camera_id, timestamp, color, type, brand, confidence
- [ ] Add to database:
  - vehicle_detections table
  - search_jobs table

### Task 4.3: Search UI
- [ ] Create `frontend/src/pages/SentinelaPage.tsx`
  - Search form: date range, cameras, filters
  - Results: timeline with matches
  - Click → jump to recording timestamp
- [ ] Create `frontend/src/components/sentinela/SearchResults.tsx`
  - Grid of detected vehicles
  - Thumbnails
  - Metadata (color, type, timestamp)

### Task 4.4: Background Processing
- [ ] Create `services/sentinela/worker.py`
  - Celery/RabbitMQ worker
  - Process search jobs async
  - Update progress in real-time
- [ ] Add WebSocket for progress updates

**Acceptance**: Busca retroativa funciona, encontra veículos em gravações

---

## 👥 PHASE 5: USER MANAGEMENT & PLANS (2 days)

### Task 5.1: Plan System
- [ ] Create `backend/apps/plans/models.py`
  - Plan: name, storage_days, max_users, price, features
  - Subscription: tenant, plan, start_date, end_date
- [ ] Create `backend/apps/plans/views.py`
  - GET /plans/ (list available plans)
  - POST /subscriptions/ (subscribe to plan)
  - GET /subscriptions/current (current plan)

### Task 5.2: User Roles
- [ ] Edit `backend/apps/usuarios/models.py`
  - Add: `role` (superadmin, user)
  - Add: `permissions` (view_only, manage_cameras, etc)
- [ ] Create permission checks:
  - Superadmin: full access
  - User: view-only, no sensitive configs
- [ ] Enforce user limits per plan

### Task 5.3: Plan UI
- [ ] Create `frontend/src/pages/PlansPage.tsx`
  - Display current plan
  - Upgrade/downgrade options
  - User management (for superadmin)
- [ ] Create `frontend/src/components/users/UserList.tsx`
  - List users
  - Add/remove users (respect plan limit)
  - Role assignment

**Acceptance**: Planos funcionam, limites de usuários respeitados

---

## 🎨 PHASE 6: UI REFACTOR (2 days)

### Task 6.1: List View
- [ ] Edit `frontend/src/pages/CamerasPage.tsx`
  - Default: list view (não grid)
  - Click camera → open individual player
  - Remove grid layout toggle
- [ ] Create `frontend/src/components/cameras/CameraList.tsx`
  - Table with: name, location, status, actions
  - Actions: view, edit, delete

### Task 6.2: Mosaico Limits
- [ ] Edit `frontend/src/pages/MosaicosPage.tsx`
  - Enforce: max 4 cameras per mosaic
  - Allow: unlimited mosaics
  - Update UI messaging
- [ ] Remove concurrent stream limits (obsoleto)

### Task 6.3: Navigation
- [ ] Add to sidebar:
  - Gravações (recordings)
  - Clipes (clips)
  - Sentinela (search)
  - Planos (plans)
- [ ] Update routing

**Acceptance**: UI refletindo nova arquitetura

---

## 🧪 PHASE 7: TESTING (2-3 days)

### Task 7.1: Recording Tests
- [ ] Test cyclic storage (7/15/30 days)
- [ ] Test clip preservation
- [ ] Test playback
- [ ] Test timeline navigation

### Task 7.2: LPR Tests
- [ ] Test detection accuracy
- [ ] Test processing speed
- [ ] Test auto-training
- [ ] Test 20-camera limit

### Task 7.3: Sentinela Tests
- [ ] Test search accuracy
- [ ] Test performance (large date ranges)
- [ ] Test concurrent searches

### Task 7.4: Integration Tests
- [ ] Test full flow: record → detect → search
- [ ] Test plan limits
- [ ] Test user permissions

**Acceptance**: All tests passing

---

## 🚀 PHASE 8: DEPLOYMENT (2 days)

### Task 8.1: Docker Optimization
- [ ] Optimize images (multi-stage builds)
- [ ] Add health checks to new services
- [ ] Configure resource limits

### Task 8.2: Documentation
- [ ] Update README.md
- [ ] Create DEPLOYMENT.md
- [ ] Create USER_GUIDE.md
- [ ] API documentation (Swagger)

### Task 8.3: Monitoring
- [ ] Add metrics for recording service
- [ ] Add metrics for LPR detection
- [ ] Add metrics for Sentinela
- [ ] Update Prometheus alerts

**Acceptance**: Sistema pronto para produção

---

## 📊 PRIORIDADES MVP

1. **Recording Service** (Phase 1) - CRÍTICO
2. **Playback & Timeline** (Phase 2) - CRÍTICO
3. **LPR Detection** (Phase 3) - CRÍTICO
4. **Sentinela** (Phase 4) - IMPORTANTE
5. **Plans & Users** (Phase 5) - IMPORTANTE
6. **UI Refactor** (Phase 6) - MÉDIO
7. **Testing** (Phase 7) - ALTO
8. **Deployment** (Phase 8) - ALTO

---

## 🎯 DECISÕES TÉCNICAS

### YOLO Legacy vs Rekognition
**Decisão**: YOLO Legacy para LPR
- ✅ Sem custo por frame
- ✅ Já treinado
- ✅ Processa gravações (não tempo real)
- ❌ Precisa GPU (T4 no Colab para treino)

### Storage
**Decisão**: Local storage + S3 backup (futuro)
- Gravações: Local (MediaMTX recordings)
- Clipes: Local + S3 (permanente)
- Detecções: PostgreSQL

### Processing
**Decisão**: Assíncrono (Celery + RabbitMQ)
- LPR: processa gravações em background
- Sentinela: busca assíncrona
- Não bloqueia UI

---

## 📝 NOTAS

- **GPU**: T4 no Google Colab para treino YOLO
- **MediaMTX**: Já grava, só precisamos gerenciar ciclo
- **Fast-Plate-OCR**: Modelo global CCT-XS funciona bem
- **Limite LPR**: 20 câmeras é viável para processar gravações
- **Sentinela**: Pode demorar, por isso é assíncrono
