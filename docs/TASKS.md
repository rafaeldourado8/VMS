# VMS Implementation Tasks

**Status**: Streaming ✅ | LPR ✅ | Recording 🔄 | Sentinela ❌ | Planos ❌

---

## ✅ CONCLUÍDO

### Infraestrutura Base
- [x] Docker Compose configurado
- [x] PostgreSQL + Redis + RabbitMQ
- [x] Prometheus monitoring
- [x] Auto-restart pipelines
- [x] Health checks

### Streaming
- [x] MediaMTX (HLS/WebRTC)
- [x] Backend API (Django)
- [x] Frontend (React + Vite)
- [x] Video Player component
- [x] Mosaicos (4 câmeras)

### LPR Detection
- [x] YOLO + Fast-Plate-OCR integrado
- [x] Lógica RTSP (ativa) vs RTMP (desativa)
- [x] Auto-treinamento
- [x] Webhook LPR
- [x] Docker service configurado

---

## 🔄 PHASE 1: RECORDING SERVICE (3-4 dias) - ATUAL

### Objetivo
Implementar gravação cíclica com planos de 7/15/30 dias e clipes permanentes.

### Task 1.1: Storage Manager
- [ ] Create `services/recording/storage_manager.py`
  ```python
  class StorageManager:
      def __init__(self, plan_days: int):
          self.plan_days = plan_days
          self.recordings = []
      
      def add_recording(self, recording):
          if len(self.recordings) >= self.plan_days:
              self.delete_oldest()  # Sobrescreve
          self.recordings.append(recording)
      
      def delete_oldest(self):
          # Deleta dia[0], exceto clipes
          pass
  ```
- [ ] Integração com MediaMTX recordings folder
- [ ] Cleanup automático

### Task 1.2: Database Models
- [ ] Edit `backend/apps/recordings/models.py`
  ```python
  class StoragePlan(models.Model):
      name = models.CharField(max_length=50)  # "7 dias", "15 dias", "30 dias"
      days = models.IntegerField()
      max_users = models.IntegerField()
      price = models.DecimalField()
  
  class Recording(models.Model):
      camera = models.ForeignKey(Camera)
      start_time = models.DateTimeField()
      end_time = models.DateTimeField()
      file_path = models.CharField(max_length=500)
      plan = models.ForeignKey(StoragePlan)
      size_mb = models.IntegerField()
  
  class Clip(models.Model):
      recording = models.ForeignKey(Recording)
      start_time = models.DateTimeField()
      end_time = models.DateTimeField()
      file_path = models.CharField(max_length=500)
      permanent = models.BooleanField(default=True)
      created_by = models.ForeignKey(User)
  ```
- [ ] Migrations

### Task 1.3: MediaMTX Recording Config
- [ ] Edit `mediamtx.yml`
  ```yaml
  paths:
    all:
      record: yes
      recordPath: /recordings/%path/%Y-%m-%d/%H-%M-%S
      recordFormat: mp4
      recordSegmentDuration: 1h
  ```
- [ ] Test recording generation

### Task 1.4: Recording Monitor
- [ ] Create `services/recording/monitor.py`
  ```python
  # Monitora pasta /recordings
  # Quando novo arquivo: registra no banco
  # Calcula tamanho
  # Atualiza status
  ```
- [ ] Add to docker-compose.yml

### Task 1.5: Cleanup Worker
- [ ] Create `services/recording/cleanup_worker.py`
  ```python
  # Cron: daily 00:00
  # Para cada câmera:
  #   - Busca recordings > plan_days
  #   - Verifica se não é clip
  #   - Deleta arquivo
  #   - Remove do banco
  ```
- [ ] Celery task

### Task 1.6: API Endpoints
- [ ] Create `backend/apps/recordings/views.py`
  ```python
  GET  /api/recordings/?camera_id=X&date=Y  # Lista gravações
  GET  /api/recordings/{id}/                # Detalhes
  POST /api/clips/                          # Cria clip
  GET  /api/clips/                          # Lista clips
  DELETE /api/clips/{id}/                   # Deleta clip
  ```

**Acceptance**: 
- Gravação contínua funciona
- Plano 7 dias deleta gravações antigas
- Clipes são preservados
- API retorna gravações por data

---

## 📺 PHASE 2: PLAYBACK & TIMELINE (2-3 dias)

### Objetivo
Permitir navegação em gravações com timeline visual.

### Task 2.1: Playback API
- [ ] Create `backend/apps/recordings/playback.py`
  ```python
  def get_playback_url(camera_id, date):
      # Retorna URL HLS da gravação
      # Converte MP4 → HLS on-demand
      pass
  ```
- [ ] HLS generator (FFmpeg)

### Task 2.2: Timeline Component
- [ ] Create `frontend/src/components/recordings/Timeline.tsx`
  - Date picker
  - Hour bar (00:00 - 23:59)
  - Recording segments (azul)
  - Clip markers (amarelo)
  - Seek bar
  - Play/Pause

### Task 2.3: Playback Player
- [ ] Create `frontend/src/components/recordings/PlaybackPlayer.tsx`
  - HLS player
  - Timeline integration
  - Speed control (1x, 2x, 4x)
  - Screenshot

### Task 2.4: Clip Creator
- [ ] Create `frontend/src/components/recordings/ClipCreator.tsx`
  - Select start time
  - Select end time
  - Preview
  - Save permanent clip
  - Generate thumbnail

### Task 2.5: Recordings Page
- [ ] Create `frontend/src/pages/RecordingsPage.tsx`
  - Camera selector
  - Date picker
  - Timeline
  - Playback player
  - Clip list

**Acceptance**:
- Timeline mostra gravações do dia
- Playback funciona
- Clipes são criados e salvos
- Navegação por data funciona

---

## 🔍 PHASE 3: SENTINELA (3-4 dias)

### Objetivo
Busca retroativa em gravações usando YOLO.

### Task 3.1: Sentinela Service
- [ ] Create `services/sentinela/detector.py`
  ```python
  class VehicleDetector:
      def __init__(self):
          self.model = YOLO('yolov8n.pt')
      
      def detect_vehicles(self, video_path):
          # Processa vídeo frame a frame
          # Detecta: cor, tipo, marca
          # Retorna: lista de detecções com timestamps
          pass
  ```

### Task 3.2: Search Engine
- [ ] Create `services/sentinela/search.py`
  ```python
  def search_vehicles(cameras, date_range, filters):
      # filters: color, type, brand, plate
      # Processa gravações
      # Retorna matches
      pass
  ```

### Task 3.3: Database Models
- [ ] Create `backend/apps/sentinela/models.py`
  ```python
  class SearchJob(models.Model):
      user = models.ForeignKey(User)
      cameras = models.ManyToManyField(Camera)
      start_date = models.DateField()
      end_date = models.DateField()
      filters = models.JSONField()
      status = models.CharField()  # pending, processing, completed
      progress = models.IntegerField()
  
  class VehicleDetection(models.Model):
      camera = models.ForeignKey(Camera)
      timestamp = models.DateTimeField()
      color = models.CharField()
      vehicle_type = models.CharField()
      brand = models.CharField()
      confidence = models.FloatField()
      image_path = models.CharField()
  ```

### Task 3.4: Background Worker
- [ ] Create `services/sentinela/worker.py`
  - Celery worker
  - Processa SearchJob async
  - Atualiza progress
  - WebSocket para updates

### Task 3.5: Search UI
- [ ] Create `frontend/src/pages/SentinelaPage.tsx`
  - Search form (cameras, dates, filters)
  - Progress bar
  - Results grid
  - Click → jump to timestamp

**Acceptance**:
- Busca retroativa funciona
- Detecta veículos em gravações
- Filtros funcionam (cor, tipo)
- Resultados clicáveis levam ao vídeo

---

## 👥 PHASE 4: PLANOS & USUÁRIOS (2 dias)

### Objetivo
Sistema de planos com limites de usuários.

### Task 4.1: Plan Models
- [ ] Create `backend/apps/plans/models.py`
  ```python
  class Plan(models.Model):
      name = models.CharField()  # "Basic", "Pro", "Premium"
      storage_days = models.IntegerField()  # 7, 15, 30
      max_users = models.IntegerField()  # 3, 5, 10
      price = models.DecimalField()
      features = models.JSONField()
  
  class Subscription(models.Model):
      tenant = models.ForeignKey(Tenant)
      plan = models.ForeignKey(Plan)
      start_date = models.DateField()
      end_date = models.DateField()
      active = models.BooleanField()
  ```

### Task 4.2: User Roles
- [ ] Edit `backend/apps/usuarios/models.py`
  ```python
  class User:
      role = models.CharField(choices=[
          ('superadmin', 'SuperAdmin'),
          ('user', 'User')
      ])
      permissions = models.JSONField()
  ```
- [ ] Permission checks
- [ ] Enforce user limits per plan

### Task 4.3: Plan UI
- [ ] Create `frontend/src/pages/PlansPage.tsx`
  - Current plan display
  - Features list
  - User count (X/Y)
  - Upgrade button

### Task 4.4: User Management
- [ ] Create `frontend/src/pages/UsersPage.tsx`
  - List users
  - Add user (check limit)
  - Remove user
  - Role assignment

**Acceptance**:
- 3 planos funcionam (7/15/30)
- Limites de usuários respeitados
- SuperAdmin gerencia usuários
- Users têm acesso view-only

---

## 🎨 PHASE 5: UI REFACTOR (2 dias)

### Objetivo
Atualizar UI para refletir nova arquitetura.

### Task 5.1: List View
- [ ] Edit `frontend/src/pages/CamerasPage.tsx`
  - Remove grid toggle
  - Default: table list
  - Columns: name, location, status, type (RTSP/RTMP), actions
  - Click row → open player

### Task 5.2: Individual Player
- [ ] Create `frontend/src/pages/CameraPlayerPage.tsx`
  - Full screen player
  - Camera info
  - Recording status
  - LPR detections (if RTSP)

### Task 5.3: Mosaico Limits
- [ ] Edit `frontend/src/pages/MosaicosPage.tsx`
  - Enforce: max 4 cameras
  - Show: "X/4 câmeras"
  - Disable add button when full

### Task 5.4: Navigation
- [ ] Edit `frontend/src/components/Sidebar.tsx`
  - Add: Gravações
  - Add: Clipes
  - Add: Sentinela
  - Add: Planos
  - Add: Usuários (superadmin only)

### Task 5.5: Dashboard
- [ ] Create `frontend/src/pages/DashboardPage.tsx`
  - Total cameras (RTSP/RTMP)
  - Storage used
  - LPR detections today
  - Recent clips

**Acceptance**:
- Lista é view padrão
- Mosaicos limitados a 4
- Navegação completa
- Dashboard informativo

---

## 🧪 PHASE 6: TESTING (2 dias)

### Task 6.1: Recording Tests
- [ ] Test cyclic storage (7/15/30 days)
- [ ] Test clip preservation
- [ ] Test storage calculation
- [ ] Test cleanup worker

### Task 6.2: LPR Tests
- [ ] Test RTSP detection
- [ ] Test RTMP skip
- [ ] Test accuracy
- [ ] Test auto-training

### Task 6.3: Sentinela Tests
- [ ] Test search accuracy
- [ ] Test performance
- [ ] Test filters
- [ ] Test concurrent searches

### Task 6.4: Integration Tests
- [ ] Test full flow: record → detect → search
- [ ] Test plan limits
- [ ] Test user permissions
- [ ] Test playback

**Acceptance**: All tests passing

---

## 🚀 PHASE 7: DEPLOYMENT (2 dias)

### Task 7.1: Docker Optimization
- [ ] Multi-stage builds
- [ ] Resource limits
- [ ] Health checks all services

### Task 7.2: Documentation
- [ ] Update README.md
- [ ] Create DEPLOYMENT.md
- [ ] Create USER_GUIDE.md
- [ ] API docs (Swagger)

### Task 7.3: Monitoring
- [ ] Metrics for recording service
- [ ] Metrics for sentinela
- [ ] Update Prometheus alerts
- [ ] Grafana dashboards

**Acceptance**: Sistema pronto para produção

---

## 📊 PRIORIDADES

### MVP (2 semanas)
1. ✅ Streaming + LPR
2. 🔄 Recording Service (Phase 1)
3. 📺 Playback & Timeline (Phase 2)
4. 🎨 UI Refactor (Phase 5)

### Completo (4 semanas)
5. 🔍 Sentinela (Phase 3)
6. 👥 Planos & Usuários (Phase 4)
7. 🧪 Testing (Phase 6)
8. 🚀 Deployment (Phase 7)

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

1. **Iniciar Phase 1: Recording Service**
   - Criar `services/recording/`
   - Implementar StorageManager
   - Configurar MediaMTX recording

2. **Testar LPR Detection**
   - Adicionar câmera RTSP real
   - Verificar detecções
   - Validar auto-treinamento

3. **Preparar Phase 2**
   - Estudar FFmpeg HLS conversion
   - Prototipar Timeline component
