# Sprint 0: Branch Setup - Resumo das Mudanças

## ✅ Tarefas Concluídas

### 1. Docker Compose
**Arquivo:** `docker-compose.yml`

**Removido:**
- Serviço `ai_detection` (completo)
- Serviço `detection_consumer` (completo)

**Resultado:** Sistema agora roda apenas com streaming básico, sem processamento de IA.

---

### 2. Backend - URLs
**Arquivo:** `backend/config/urls.py`

**Removido:**
- `path("api/", include("apps.deteccoes.urls"))` - Rotas de detecções
- Rotas temporárias de AI:
  - `/api/ai/cameras/<pk>/start/`
  - `/api/ai/cameras/<pk>/stop/`
  - `/api/ai/cameras/<pk>/status/`

**Resultado:** API não expõe mais endpoints de detecção ou controle de IA.

---

### 3. Backend - Camera Views
**Arquivo:** `backend/apps/cameras/views.py`

**Removido:**
- Lógica de ativação automática de IA no método `create()`
- Notificação para LPR service via HTTP
- Actions de controle de IA:
  - `toggle_ai()`
  - `start_ai()`
  - `stop_ai()`
  - `ai_status()`

**Resultado:** Câmeras são criadas sem qualquer integração com IA.

---

### 4. Backend - Requirements
**Arquivo:** `backend/requirements.txt`

**Status:** Nenhuma dependência de IA foi encontrada (já estava limpo).

**Mantido:**
- Django, DRF, PostgreSQL, Redis, Celery
- Dependências de produção e testes

---

### 5. Frontend - Rotas
**Arquivo:** `frontend/src/App.tsx`

**Removido:**
- Import de `DetectionsPage`
- Rota `/detections`

**Resultado:** Aplicação não tem mais página de detecções.

---

### 6. Frontend - Menu de Navegação
**Arquivo:** `frontend/src/components/layout/Layout.tsx`

**Removido:**
- Item de menu "Detecções" com ícone `Car`

**Resultado:** Menu lateral não mostra mais opção de detecções.

---

### 7. Variáveis de Ambiente
**Arquivo:** `.env.example`

**Removido:**
- `ADMIN_API_KEY` (LPR Detection)
- `DETECTION_CONFIDENCE_THRESHOLD`
- Todas as variáveis de AI Detection:
  - `USE_WEBRTC`, `AI_FPS`, `MOTION_THRESHOLD`
  - `MOG2_VAR_THRESHOLD`, `MOG2_HISTORY`
  - `VEHICLE_CONFIDENCE`, `VEHICLE_MODEL`
  - `TRACKER_IOU_THRESHOLD`, `TRACKER_TIMEOUT`
  - `QUALITY_WEIGHT_*` (blur, angle, contrast, size)
  - `MIN_QUALITY_SCORE`
  - `PLATE_CONFIDENCE`, `PLATE_MODEL`
  - `OCR_MODEL`
  - `MIN_READINGS`, `MAX_READINGS`
  - `CONSENSUS_THRESHOLD`, `SIMILARITY_THRESHOLD`
  - `MIN_CONFIDENCE`, `DEDUP_TTL`

**Adicionado:**
- `RECORDING_FORMAT=mp4`
- `RECORDING_SEGMENT_DURATION=3600`
- `MAX_CLIP_DURATION=300`
- `RECORDING_RETENTION_DAYS=7`
- `S3_BUCKET=vms-recordings` (alterado de vms-detections)
- `MAX_CAMERAS_PER_USER=20` (alterado de 4)

**Resultado:** Configuração focada em DVR, não em IA.

---

## 📊 Impacto

### Serviços Removidos
- ❌ AI Detection Service (WebRTC + Pipeline)
- ❌ Detection Consumer (RabbitMQ)

### Serviços Mantidos
- ✅ Backend (Django API)
- ✅ Frontend (React + Vite)
- ✅ Streaming (MediaMTX)
- ✅ PostgreSQL
- ✅ Redis
- ✅ RabbitMQ (para futuras tasks de gravação)
- ✅ Prometheus

### Funcionalidades Removidas
- ❌ Detecção de placas (LPR)
- ❌ Dashboard de detecções em tempo real
- ❌ WebSocket de detecções
- ❌ Controle de IA por câmera
- ❌ ROI e configurações de detecção

### Funcionalidades Mantidas
- ✅ Streaming HLS
- ✅ Gerenciamento de câmeras
- ✅ Autenticação e autorização
- ✅ Multi-tenant
- ✅ Thumbnails
- ✅ Paginação de câmeras

---

## 🧪 Próximos Passos

### Testes Necessários
1. Verificar que o sistema sobe sem erros:
   ```bash
   docker-compose up -d
   docker-compose ps
   ```

2. Testar streaming de câmeras:
   - Adicionar câmera RTSP/RTMP
   - Verificar que HLS funciona
   - Confirmar que thumbnails são gerados

3. Testar API:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/api/cameras/
   ```

4. Testar frontend:
   - Login
   - Visualizar câmeras
   - Navegar entre páginas
   - Confirmar que não há erros de console

### Commit
Após testes bem-sucedidos:
```bash
git add .
git commit -m "chore: setup dvr-lite branch - remove AI detection services"
```

---

## 📝 Notas

### Arquivos Não Modificados (mas podem ser removidos depois)
- `backend/apps/deteccoes/` - App completo de detecções
- `backend/application/detection/` - Handlers de detecção
- `backend/domain/detection/` - Entidades de detecção
- `frontend/src/pages/DetectionsPage.tsx` - Página de detecções
- `frontend/src/components/detections/` - Componentes de detecção

**Decisão:** Manter por enquanto para não quebrar imports. Remover em limpeza futura se necessário.

### Dependências do RabbitMQ
RabbitMQ foi mantido porque será usado para:
- Processamento assíncrono de clipes
- Limpeza automática de gravações
- Notificações futuras

---

## 🎯 Objetivo Alcançado

Sistema agora é um **DVR puro**:
- ✅ Streaming de câmeras
- ✅ Gerenciamento básico
- ❌ Sem IA
- ❌ Sem detecções
- 🔜 Pronto para adicionar gravação (Sprint 1)
