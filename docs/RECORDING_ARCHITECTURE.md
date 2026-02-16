# Arquitetura de Gravação - VMS

## Visão Geral

Sistema distribuído de gravação com microserviços FastAPI e Django Apps para gerenciar gravações de vídeo, timeline, retenção e storage.

---

## 🎯 Componentes e Responsabilidades

### 1. **RECORDER** (FastAPI Service)
**Localização:** `services/recorder/recorder.py`

**Responsabilidade:**
- Grava streams RTSP em segmentos de 60 segundos
- Monitora câmeras ativas via Django API
- Auto-recuperação de processos FFmpeg
- Organiza arquivos por câmera e data

**Comunicação:**
- **Consome:** Django API (`/api/cameras/recorder/`)
- **Produz:** Arquivos MP4 em `/recordings/camera_{id}/{date}/{HH-MM-SS}.mp4`

**Estrutura de Dados:**
```
/recordings/
├── camera_1/
│   └── 2026-02-13/
│       ├── 10-00-00.mp4  (60s)
│       ├── 10-01-00.mp4  (60s)
│       └── 10-02-00.mp4  (60s)
```

**Fluxo:**
1. Busca câmeras online do Django
2. Inicia FFmpeg para cada câmera
3. Grava segmentos de 60s
4. Monitora processos a cada 30s
5. Reinicia processos mortos

---

### 2. **RETENTION_CLEANUP** (FastAPI Service)
**Localização:** `services/recorder/retention_cleanup.py`

**Responsabilidade:**
- Limpeza automática de gravações antigas (FIFO)
- Executa a cada 1 hora
- Respeita política de retenção por câmera

**Comunicação:**
- **Consome:** Django API (`/api/cameras/recorder/`)
- **Deleta:** Arquivos MP4 expirados

**Política FIFO:**
```python
# Exemplo: Retenção de 7 dias
cutoff_date = today - timedelta(days=7)
# Deleta tudo antes de cutoff_date
```

**Fluxo:**
1. Busca políticas de retenção do Django
2. Calcula data de corte (hoje - retention_days)
3. Varre diretórios de gravação
4. Deleta pastas antigas
5. Loga estatísticas

---

### 3. **RECORDING** (FastAPI Service)
**Localização:** `services/recording/main.py`

**Responsabilidade:**
- API para listar gravações
- Validação de integridade (ffprobe)
- Notificação ao Django sobre novas gravações

**Endpoints:**
- `GET /recordings/{camera_id}` - Lista gravações
- `POST /recordings/{camera_id}/validate` - Valida integridade
- `POST /recordings/{camera_id}/notify` - Notifica Django

**Comunicação:**
- **Lê:** Sistema de arquivos `/recordings`
- **Notifica:** Django API (`/api/recordings/`)

---

### 4. **STORAGE** (FastAPI Service)
**Localização:** `services/storage/main.py`

**Responsabilidade:**
- Indexa gravações em banco PostgreSQL
- Query de segmentos por intervalo de tempo
- Marca segmentos como processados (LPR)

**Modelo de Dados:**
```sql
CREATE TABLE recording_segments (
    id SERIAL PRIMARY KEY,
    camera_id INTEGER NOT NULL,
    file_path TEXT NOT NULL UNIQUE,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    duration_seconds INTEGER NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Endpoints:**
- `POST /recordings/query` - Query por intervalo
- `POST /recordings/mark-processed` - Marca como processado
- `GET /recordings/stats` - Estatísticas

**Fluxo de Indexação:**
1. Scan a cada 60s em `/recordings`
2. Parse filename: `HH-MM-SS.mp4`
3. Calcula start_time e end_time
4. Insere no banco (ON CONFLICT DO NOTHING)

---

### 5. **TIMELINE** (FastAPI Service)
**Localização:** `services/timeline/main.py`

**Responsabilidade:**
- Constrói timeline de gravações por câmera
- Detecta gaps (períodos sem gravação)
- Cache de timelines
- Resolve timestamp → arquivo de vídeo

**Endpoints:**
- `GET /timeline/{camera_id}` - Timeline completa
- `GET /timeline/{camera_id}/blocks` - Blocos de gravação
- `GET /video/{camera_id}/{timestamp}` - Resolve vídeo por timestamp
- `POST /reindex/{camera_id}` - Força reindexação
- `POST /cleanup-notification` - Webhook de cleanup

**Modelo de Timeline:**
```python
{
  "camera_id": 1,
  "blocks": [
    {
      "start_time": "2026-02-13T10:00:00Z",
      "end_time": "2026-02-13T10:05:00Z",
      "duration": 300,
      "file_size": 15728640,
      "has_gaps": false
    }
  ],
  "total_duration": 300,
  "coverage_percent": 100.0
}
```

---

### 6. **Django App: recordings**
**Localização:** `backend/apps/recordings/`

**Responsabilidade:**
- Modelo de dados de gravações
- API REST para frontend
- Sincronização com Recording Service

**Modelo:**
```python
class Recording(models.Model):
    camera_id = models.IntegerField()
    date = models.DateField()
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=512)
    size_mb = models.FloatField()
    duration_min = models.FloatField()
    codec = models.CharField(max_length=50)
    is_valid = models.BooleanField()
```

**Endpoints:**
- `GET /api/recordings/` - Lista gravações
- `GET /api/recordings/by_camera/` - Por câmera
- `POST /api/recordings/sync_from_service/` - Sincroniza

---

### 7. **Django App: timeline**
**Localização:** `backend/apps/timeline/`

**Responsabilidade:**
- Gerenciamento de políticas de retenção
- Auditoria de storage
- Cleanup de gravações antigas
- Estatísticas de uso

**Modelos:**
```python
class RetentionPlan(models.Model):
    name = models.CharField(max_length=100)
    days = models.IntegerField()
    is_active = models.BooleanField()

class CameraRetention(models.Model):
    camera = models.OneToOneField(Camera)
    retention_plan = models.ForeignKey(RetentionPlan)
    custom_days = models.IntegerField(null=True)
    enabled = models.BooleanField()

class StorageAudit(models.Model):
    camera = models.ForeignKey(Camera)
    action = models.CharField(max_length=20)  # created, deleted, expired
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    timestamp = models.DateTimeField()
```

**Serviços:**
- `RetentionService` - Cálculo de retenção
- `StorageService` - Estatísticas de storage
- `CleanupService` - Limpeza de arquivos

**Endpoints:**
- `GET /api/timeline/retention-plans/` - Planos de retenção
- `GET /api/timeline/storage/stats/` - Estatísticas
- `GET /api/timeline/storage/cameras/` - Uso por câmera
- `GET /api/timeline/audit/` - Logs de auditoria

---

## 🔄 Fluxo de Dados Completo

### Gravação
```
1. RECORDER → FFmpeg → /recordings/camera_1/2026-02-13/10-00-00.mp4
2. STORAGE → Scan → PostgreSQL (recording_segments)
3. TIMELINE → Index → Cache (timeline blocks)
```

### Consulta
```
1. Frontend → Django API → /api/recordings/by_camera/?camera_id=1
2. Django → Timeline Service → /timeline/1
3. Timeline → Resolve blocks → Return JSON
4. Frontend → Renderiza player com barra de progresso
```

### Cleanup
```
1. RETENTION_CLEANUP → Django API → Busca políticas
2. Calcula cutoff_date (hoje - retention_days)
3. Deleta arquivos antigos
4. Django → Timeline Service → /cleanup-notification
5. Timeline → Invalida cache → Reindex
```

---

## ⚠️ Problemas Identificados

### 1. **Falta de Orquestração**
- Serviços não se comunicam diretamente
- Sem coordenação entre RECORDER, STORAGE e TIMELINE
- Cleanup não notifica Timeline automaticamente

### 2. **Duplicação de Lógica**
- Django e FastAPI têm lógicas similares
- Scan de arquivos duplicado (Storage + Timeline)

### 3. **Falta de Sincronização**
- Timeline pode ficar desatualizado
- Storage pode ter índices órfãos

### 4. **Sem Transações Distribuídas**
- Cleanup pode deletar arquivo mas falhar ao atualizar banco
- Sem rollback em caso de erro

---

## ✅ Solução: Serviço Orquestrador

Criar **Recording Orchestrator** (FastAPI) para:

1. **Coordenar gravação**
   - Notificar Storage quando novo arquivo é criado
   - Notificar Timeline para reindexar

2. **Coordenar cleanup**
   - Deletar arquivo
   - Atualizar Storage
   - Invalidar cache Timeline
   - Tudo em transação

3. **Health checks**
   - Monitorar todos os serviços
   - Auto-recovery

4. **Event Bus**
   - Publicar eventos: `recording.created`, `recording.deleted`
   - Serviços subscrevem eventos

---

## 📊 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    RECORDING ORCHESTRATOR                    │
│                      (FastAPI - Port 8010)                   │
│  - Coordena gravação, indexação, cleanup                    │
│  - Event Bus (Redis Pub/Sub)                                │
│  - Health checks de todos os serviços                       │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    RECORDER     │  │     STORAGE     │  │    TIMELINE     │
│   (Port 8000)   │  │   (Port 8003)   │  │   (Port 8007)   │
│  - Grava vídeos │  │  - Indexa DB    │  │  - Constrói     │
│  - FFmpeg       │  │  - PostgreSQL   │  │    timeline     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                    ┌─────────────────┐
                    │   /recordings   │
                    │  (File System)  │
                    └─────────────────┘
                              ▲
                              │
                    ┌─────────────────┐
                    │ RETENTION       │
                    │ CLEANUP         │
                    │ - Deleta antigos│
                    └─────────────────┘
```

---

## 🎯 Próximos Passos

1. ✅ Documentar arquitetura atual
2. 🔨 Criar Recording Orchestrator
3. 🔨 Implementar Event Bus (Redis)
4. 🔨 Integrar Timeline com player
5. 🔨 Criar barra de progresso com gaps
