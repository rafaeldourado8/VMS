# 📊 Sprint 0: Mudanças Visuais

## Antes vs Depois

### Arquitetura de Serviços

#### ANTES (VMS Full)
```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│              React + Detections Dashboard                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                            │
│         /api/detections/ + /api/ai/cameras/                 │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┬─────────────┐
                ▼             ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
         │PostgreSQL│  │  Redis   │  │ RabbitMQ │  │MediaMTX  │
         └──────────┘  └──────────┘  └──────────┘  └──────────┘
                                            │             │
                              ┌─────────────┼─────────────┘
                              ▼             ▼
                    ┌──────────────┐  ┌──────────────┐
                    │AI Detection  │  │  Detection   │
                    │   Service    │  │  Consumer    │
                    │(YOLO + OCR)  │  │  (RabbitMQ)  │
                    └──────────────┘  └──────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  RTSP Cameras   │
                    │   (LPR Only)    │
                    └─────────────────┘
```

#### DEPOIS (DVR-Lite)
```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    React (Clean UI)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                            │
│                  /api/cameras/ only                         │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │PostgreSQL│  │  Redis   │  │ RabbitMQ │
         └──────────┘  └──────────┘  └──────────┘
                                            │
                                            ▼
                                      ┌──────────┐
                                      │MediaMTX  │
                                      └──────────┘
                                            │
                                            ▼
                                  ┌─────────────────┐
                                  │ RTSP/RTMP       │
                                  │ Cameras         │
                                  │ (All Types)     │
                                  └─────────────────┘
```

---

## Menu de Navegação

### ANTES
```
┌─────────────────────────┐
│  GT-Vision              │
├─────────────────────────┤
│ 📊 Dashboard            │
│ 📹 Câmeras              │
│ 🚗 Detecções           │  ← REMOVIDO
│ ✂️  Meus Clips          │
│ 🔲 Mosaicos             │
│ ⚙️  Configurações       │
└─────────────────────────┘
```

### DEPOIS
```
┌─────────────────────────┐
│  GT-Vision              │
├─────────────────────────┤
│ 📊 Dashboard            │
│ 📹 Câmeras              │
│ ✂️  Meus Clips          │
│ 🔲 Mosaicos             │
│ ⚙️  Configurações       │
└─────────────────────────┘
```

---

## Rotas da API

### ANTES
```
/api/auth/login/          ✅
/api/auth/me/             ✅
/api/cameras/             ✅
/api/detections/          ❌ REMOVIDO
/api/ai/cameras/1/start/  ❌ REMOVIDO
/api/ai/cameras/1/stop/   ❌ REMOVIDO
/api/ai/cameras/1/status/ ❌ REMOVIDO
/api/clips/               ✅
/api/dashboard/           ✅
```

### DEPOIS
```
/api/auth/login/          ✅
/api/auth/me/             ✅
/api/cameras/             ✅
/api/clips/               ✅
/api/dashboard/           ✅
```

---

## Variáveis de Ambiente

### ANTES (.env.example)
```bash
# Database (5 vars)
POSTGRES_DB=...
POSTGRES_USER=...
...

# Redis (1 var)
REDIS_URL=...

# RabbitMQ (3 vars)
RABBITMQ_USER=...
...

# AWS (3 vars)
AWS_ACCESS_KEY_ID=...
...

# MediaMTX (6 vars)
MEDIAMTX_API_USER=...
...

# JWT (3 vars)
JWT_SECRET=...
...

# App (5 vars)
DEBUG=...
MAX_CAMERAS_PER_USER=4
...

# LPR Detection (1 var)
ADMIN_API_KEY=...          ❌ REMOVIDO

# AI Detection (30 vars)    ❌ REMOVIDO
USE_WEBRTC=...
AI_FPS=...
MOTION_THRESHOLD=...
MOG2_VAR_THRESHOLD=...
VEHICLE_CONFIDENCE=...
VEHICLE_MODEL=...
PLATE_CONFIDENCE=...
PLATE_MODEL=...
OCR_MODEL=...
...

Total: ~57 variáveis
```

### DEPOIS (.env.example)
```bash
# Database (5 vars)
POSTGRES_DB=...
POSTGRES_USER=...
...

# Redis (1 var)
REDIS_URL=...

# RabbitMQ (3 vars)
RABBITMQ_USER=...
...

# AWS (3 vars)
AWS_ACCESS_KEY_ID=...
S3_BUCKET=vms-recordings  ← ALTERADO
...

# MediaMTX (6 vars)
MEDIAMTX_API_USER=...
...

# JWT (3 vars)
JWT_SECRET=...
...

# App (4 vars)
DEBUG=...
MAX_CAMERAS_PER_USER=20   ← ALTERADO (era 4)
RECORDING_RETENTION_DAYS=7 ← NOVO
...

# Recording (3 vars)        ← NOVO
RECORDING_FORMAT=mp4
RECORDING_SEGMENT_DURATION=3600
MAX_CLIP_DURATION=300

Total: ~28 variáveis (-29)
```

---

## Fluxo de Criação de Câmera

### ANTES
```
1. Usuário cria câmera RTSP
2. Backend salva no banco
3. Backend ativa AI automaticamente (ai_enabled=true)
4. Backend notifica LPR Service via HTTP
5. LPR Service inicia detecção
6. Detecções enviadas via RabbitMQ
7. Detection Consumer salva no banco
8. Frontend mostra detecções via WebSocket
```

### DEPOIS
```
1. Usuário cria câmera RTSP/RTMP
2. Backend salva no banco
3. Fim
```

---

## Docker Compose

### ANTES
```yaml
services:
  ai_detection:           ❌ REMOVIDO
    build: ./services/ai_detection
    ports: ["5000:5000"]
    volumes:
      - ./services/ai_detection/models:/app/models
      - ./detections:/app/detections
    
  detection_consumer:     ❌ REMOVIDO
    build: ./backend
    command: python backend/start_consumer.py
    
  backend:                ✅ MANTIDO
  frontend:               ✅ MANTIDO
  mediamtx:               ✅ MANTIDO
  postgres_db:            ✅ MANTIDO
  redis_cache:            ✅ MANTIDO
  rabbitmq:               ✅ MANTIDO
  prometheus:             ✅ MANTIDO
  streaming:              ✅ MANTIDO
  kong:                   ✅ MANTIDO
  haproxy:                ✅ MANTIDO
```

### DEPOIS
```yaml
services:
  backend:                ✅
  frontend:               ✅
  mediamtx:               ✅
  postgres_db:            ✅
  redis_cache:            ✅
  rabbitmq:               ✅
  prometheus:             ✅
  streaming:              ✅
  kong:                   ✅
  haproxy:                ✅
```

---

## Métricas de Código

### Arquivos Modificados
```
docker-compose.yml              -45 linhas
backend/requirements.txt         0 linhas (já limpo)
backend/config/urls.py          -8 linhas
backend/apps/cameras/views.py   -35 linhas
.env.example                    -29 variáveis
frontend/src/App.tsx            -2 linhas
frontend/src/components/layout/Layout.tsx  -1 linha

Total: ~120 linhas removidas
```

### Arquivos Criados (Documentação)
```
docs/dvr-lite/README.md                     +200 linhas
docs/dvr-lite/SPRINT0_SUMMARY.md            +150 linhas
docs/dvr-lite/SPRINT0_EXECUTIVE_SUMMARY.md  +100 linhas
docs/dvr-lite/TESTING_GUIDE.md              +300 linhas
docs/dvr-lite/GIT_COMMANDS.md               +80 linhas
docs/dvr-lite/VISUAL_CHANGES.md             +250 linhas (este arquivo)

Total: ~1080 linhas de documentação
```

---

## Complexidade

### ANTES
```
Serviços Docker:     12
Serviços de IA:      2
Variáveis de Env:    57
Rotas de API:        ~30
Páginas Frontend:    8
Componentes IA:      5
```

### DEPOIS
```
Serviços Docker:     10  (-17%)
Serviços de IA:      0   (-100%)
Variáveis de Env:    28  (-51%)
Rotas de API:        ~25 (-17%)
Páginas Frontend:    7   (-13%)
Componentes IA:      0   (-100%)
```

---

## Próximos Passos

```
Sprint 0 (Atual)
    ↓
    ✅ Limpeza de código
    ✅ Documentação
    ↓
Sprint 1 (Próximo)
    ↓
    🔄 Recording Service
    🔄 Storage S3
    🔄 Limpeza automática
    ↓
Sprint 2
    ↓
    📋 Playback API
    📋 Timeline Component
    📋 Video Player
    ↓
Sprint 3
    ↓
    ✂️ Clip System
    ✂️ Clip Processing
    ✂️ Clip Management
    ↓
Sprint 4
    ↓
    👥 Multi-usuário
    👥 Permissões
    👥 Sub-users
    ↓
Sprint 5
    ↓
    ☁️ Deploy AWS
    ☁️ CI/CD
    ☁️ Monitoring
```

---

## Resumo Visual

```
┌─────────────────────────────────────────────────────────────┐
│                    ANTES (VMS Full)                         │
├─────────────────────────────────────────────────────────────┤
│  Frontend: 8 páginas (com Detecções)                       │
│  Backend: 30 rotas (com AI)                                │
│  Serviços: 12 containers (com AI Detection)                │
│  Env Vars: 57 variáveis (30 de IA)                         │
│  Foco: Streaming + IA + Gravação                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  TRANSFORMAÇÃO  │
                    │   (Sprint 0)    │
                    └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   DEPOIS (DVR-Lite)                         │
├─────────────────────────────────────────────────────────────┤
│  Frontend: 7 páginas (sem Detecções)                       │
│  Backend: 25 rotas (sem AI)                                │
│  Serviços: 10 containers (sem AI Detection)                │
│  Env Vars: 28 variáveis (0 de IA)                          │
│  Foco: Streaming + Gravação                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Checklist Visual

```
Sprint 0: Branch Setup
├── ✅ Remover ai_detection service
├── ✅ Remover detection_consumer service
├── ✅ Remover rotas de detecção
├── ✅ Remover lógica de IA
├── ✅ Remover página de Detecções
├── ✅ Remover menu de Detecções
├── ✅ Atualizar .env.example
├── ⏳ Testar streaming
└── ⏳ Commit

Sprint 1: Recording Service
├── ⏳ Recording Service
├── ⏳ Storage S3
├── ⏳ Limpeza automática
└── ⏳ API de gravações

Sprint 2: Playback & Timeline
├── ⏳ Playback API
├── ⏳ Video Player
└── ⏳ Timeline Component

Sprint 3: Clip System
├── ⏳ Clip API
├── ⏳ Clip Processing
└── ⏳ Clip Management

Sprint 4: Multi-Usuário
├── ⏳ Sub-users
└── ⏳ Permissões

Sprint 5: Deploy AWS
├── ⏳ Infraestrutura
├── ⏳ CI/CD
└── ⏳ Monitoring
```
