# 🎬 Sprint 3: Recording & Playback

**Duração:** 2 semanas  
**Período:** Semana 5-6  
**Status:** 🔄 Em Andamento  
**Prioridade:** ALTA (antes da IA)

---

## 🎯 Objetivo

Implementar sistema completo de gravação contínua e reprodução de vídeos com timeline interativa, respeitando planos de usuário e multi-tenancy.

---

## 📋 Tasks

### 1. Recording Service (Backend)
**Prioridade:** P0 - Crítica  
**Estimativa:** 3 dias

- [ ] Service de gravação contínua (FFmpeg)
- [ ] Segmentação em arquivos de 1h (.mp4)
- [ ] Limpeza automática por plano (7/15/30 dias)
- [ ] API de listagem de gravações
- [ ] Health check e monitoring

**Entregável:** Gravações funcionando 24/7

---

### 2. Clips System (Backend)
**Prioridade:** P0 - Crítica  
**Estimativa:** 2 dias

- [ ] Model Clip (câmera, início, fim, usuário)
- [ ] API CRUD de clipes
- [ ] Extração de segmento de vídeo
- [ ] Clipes permanentes (não deletados no ciclo)
- [ ] Validação de permissões por plano

**Entregável:** Sistema de clipes funcionando

---

### 3. Playback API (Backend)
**Prioridade:** P0 - Crítica  
**Estimativa:** 2 dias

- [ ] Endpoint de busca de gravações (câmera + data)
- [ ] Streaming de gravações via HLS
- [ ] Listagem de dias disponíveis
- [ ] Cálculo de dias restantes por plano
- [ ] Integração com MediaMTX

**Entregável:** API de playback completa

---

### 4. Timeline Component (Frontend)
**Prioridade:** P0 - Crítica  
**Estimativa:** 3 dias

- [ ] Modal fullscreen ao duplo clique
- [ ] Player de vídeo (HLS.js ou Video.js)
- [ ] Controles: play, pause, seek, volume
- [ ] Barra de progresso interativa
- [ ] Seletor de data/hora
- [ ] Indicador de dias disponíveis

**Entregável:** Timeline funcional

---

### 5. Clip Creator (Frontend)
**Prioridade:** P1 - Alta  
**Estimativa:** 2 dias

- [ ] Interface de seleção início/fim
- [ ] Preview do clipe
- [ ] Botão salvar clipe
- [ ] Lista de clipes salvos
- [ ] Download de clipes

**Entregável:** Criação de clipes no frontend

---

### 6. Django Admin Integration
**Prioridade:** P1 - Alta  
**Estimativa:** 1 dia

- [ ] ModelAdmin para Recording
- [ ] ModelAdmin para Clip
- [ ] Filtros (câmera, data, usuário, plano)
- [ ] Ações bulk (deletar, exportar)
- [ ] Estatísticas de armazenamento

**Entregável:** Gestão via admin panel

---

### 7. Storage Management
**Prioridade:** P0 - Crítica  
**Estimativa:** 2 dias

- [ ] Cron job de limpeza automática
- [ ] Cálculo de espaço usado por usuário
- [ ] Alertas de espaço (80%, 90%, 95%)
- [ ] Compressão de vídeos antigos
- [ ] Logs de limpeza

**Entregável:** Storage gerenciado automaticamente

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                    Frontend                          │
│  ┌──────────────┐         ┌──────────────┐         │
│  │ Camera Grid  │ ──2x──> │   Timeline   │         │
│  │  (Duplo      │  click  │   Component  │         │
│  │   clique)    │         │              │         │
│  └──────────────┘         └──────┬───────┘         │
│                                   │                  │
│                          ┌────────▼────────┐        │
│                          │  Clip Creator   │        │
│                          └─────────────────┘        │
└──────────────────────────────┬──────────────────────┘
                               │ HTTP/WebSocket
┌──────────────────────────────▼──────────────────────┐
│                    Backend API                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Playback    │  │    Clips     │  │ Recording │ │
│  │     API      │  │     API      │  │    API    │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
└─────────┼──────────────────┼────────────────┼───────┘
          │                  │                │
┌─────────▼──────────────────▼────────────────▼───────┐
│              Recording Service (Python)              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   FFmpeg     │  │   Storage    │  │  Cleanup  │ │
│  │  Recorder    │  │  Management  │  │   Cron    │ │
│  └──────┬───────┘  └──────────────┘  └───────────┘ │
└─────────┼──────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────┐
│                   MediaMTX                          │
│              (Streaming Server)                     │
└─────────┬──────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────┐
│                Storage (Volume)                     │
│  /recordings/                                       │
│    /cidade_1/                                       │
│      /cam_1/                                        │
│        /2026-01-14/                                 │
│          00-00-00.mp4 (1h)                         │
│          01-00-00.mp4                              │
│          ...                                        │
│    /clips/                                          │
│      /cam_1/                                        │
│        clip_123.mp4 (permanente)                   │
└────────────────────────────────────────────────────┘
```

---

## 💾 Estrutura de Dados

### Model: Recording
```python
class Recording(models.Model):
    camera = ForeignKey(Camera)
    start_time = DateTimeField()
    end_time = DateTimeField()
    file_path = CharField()
    file_size = BigIntegerField()  # bytes
    duration = IntegerField()  # segundos
    created_at = DateTimeField(auto_now_add=True)
```

### Model: Clip
```python
class Clip(models.Model):
    camera = ForeignKey(Camera)
    user = ForeignKey(Usuario)
    name = CharField(max_length=255)
    start_time = DateTimeField()
    end_time = DateTimeField()
    file_path = CharField()
    file_size = BigIntegerField()
    is_permanent = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
```

---

## 🎨 Interface (Timeline)

```
┌─────────────────────────────────────────────────────────────┐
│  ✕  📹 Câmera 1 - Entrada Principal                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                        │ │
│  │              [PLAYER DE VÍDEO]                        │ │
│  │                                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  [⏮️] [▶️] [⏸️] [⏭️]  🔊 ━━━━━━━━━━━━━━━━━━━  [⚙️] [⛶]   │
│                                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  00:00        06:00        12:00        18:00        24:00  │
│  │             │            │            │             │     │
│  🔴           🔴          🔴🔴         🔴            🔴    │
│  (Marcadores de detecções LPR)                              │
│                                                              │
│  📅 14/01/2026  [◀ Dia Anterior] [Próximo Dia ▶]           │
│  📊 Dia 3 de 7 disponíveis (Plano Basic)                    │
│                                                              │
│  ✂️ [Criar Clipe]  📋 [Ver Clipes Salvos]                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Planos e Limites

| Plano | Dias | Usuários | Storage/Câmera | Clipes |
|-------|------|----------|----------------|--------|
| Basic | 7 | 3 | ~168 GB | 10 |
| Pro | 15 | 5 | ~360 GB | 50 |
| Premium | 30 | 10 | ~720 GB | Ilimitado |

**Cálculo Storage:**
- 1 câmera 1080p @ 2Mbps = ~900MB/hora
- 24h = ~21.6GB/dia
- 7 dias = ~151GB
- 10 câmeras = ~1.5TB

---

## 🔧 Tecnologias

### Backend
- **FFmpeg** - Gravação e processamento
- **Celery** - Jobs assíncronos (limpeza)
- **Django ORM** - Models e queries

### Frontend
- **Video.js** ou **HLS.js** - Player
- **React Player** - Wrapper React
- **date-fns** - Manipulação de datas

### Storage
- **Docker Volume** - Persistência
- **H.264** - Codec de vídeo
- **MP4** - Container

---

## ✅ Critérios de Aceitação

### Recording
- ✅ Gravação 24/7 sem perda de frames
- ✅ Segmentos de 1h funcionando
- ✅ Limpeza automática por plano
- ✅ 0 downtime durante limpeza

### Playback
- ✅ Latência <2s para iniciar
- ✅ Seek funciona corretamente
- ✅ Marcadores de detecções visíveis
- ✅ Seletor de data funcional

### Clips
- ✅ Criação em <5s
- ✅ Clipes não deletados no ciclo
- ✅ Download funciona
- ✅ Limites por plano respeitados

### Admin
- ✅ Visualização de todas gravações
- ✅ Filtros funcionando
- ✅ Estatísticas corretas
- ✅ Ações bulk funcionando

---

## 🧪 Testes

### Unitários
```bash
# Backend
pytest backend/tests/test_recording.py
pytest backend/tests/test_clips.py
pytest backend/tests/test_playback.py

# Frontend
npm test -- Timeline.test.tsx
npm test -- ClipCreator.test.tsx
```

### Integração
```bash
# E2E
npm run test:e2e -- recording-playback.spec.ts
```

### Performance
```bash
# Load test
locust -f tests/load/recording_load.py
```

---

## 📈 Métricas de Sucesso

### Performance
- Gravação: 0 frames perdidos
- Playback: <2s latência
- Seek: <500ms resposta
- Clip creation: <5s

### Storage
- Limpeza automática: 100% efetiva
- Compressão: >50% economia
- Alertas: 0 falsos positivos

### UX
- Timeline load: <1s
- Player controls: <100ms resposta
- Clip preview: <2s

---

## 🚀 Deploy

### 1. Build Recording Service
```bash
cd services/recording
docker build -t vms/recording:latest .
```

### 2. Update docker-compose.yml
```yaml
recording:
  image: vms/recording:latest
  volumes:
    - recordings:/recordings
  environment:
    - RETENTION_DAYS=${RETENTION_DAYS}
```

### 3. Migrate Database
```bash
docker exec backend python manage.py migrate
```

### 4. Start Services
```bash
docker-compose up -d recording
```

---

## 📝 Documentação Relacionada

- [Recording Service](./recording-service/README.md)
- [Playback API](./playback-api/README.md)
- [Timeline Component](./timeline-component/README.md)
- [Clip System](./clip-system/README.md)
- [Storage Management](./storage-management/README.md)

---

## 🔄 Próximos Passos

Após conclusão do Sprint 3:
1. Sprint 4: Deploy & Produção
2. Fase 5: Multi-Tenant completo
3. Fase 6: Analytics & Relatórios
4. Fase 7: Sentinela (Busca Retroativa)

---

**Criado:** 2026-01-14  
**Última atualização:** 2026-01-14  
**Responsável:** Dev Team
