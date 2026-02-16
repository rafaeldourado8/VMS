# Timeline Service - Arquitetura Técnica

## Visão Geral da Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │  Django App     │    │ FastAPI Service │
│   (React)       │    │  (Timeline)     │    │  (Indexer)      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Timeline UI   │◄──►│ • Retention API │◄──►│ • File Indexing │
│ • Player        │    │ • Storage Stats │    │ • Timeline Gen  │
│ • Config Panel  │    │ • Audit Logs    │    │ • Video Resolve │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   Filesystem    │
                       │   (Config/Logs) │    │   (Recordings)  │
                       └─────────────────┘    └─────────────────┘
```

## Componentes Detalhados

### 1. FastAPI Service (Port 8007)

**Responsabilidades:**
- Indexação de arquivos de gravação
- Geração de timeline por câmera
- Resolução de timestamp para arquivo
- Cache de índices em memória
- Processamento assíncrono

**Endpoints Principais:**
```
GET  /timeline/{camera_id}           # Timeline completa
GET  /timeline/{camera_id}/blocks    # Blocos de gravação
GET  /video/{camera_id}/{timestamp}  # Resolve vídeo por timestamp
POST /reindex/{camera_id}            # Força reindexação
GET  /health                         # Health check
```

**Estrutura de Dados:**
```python
TimelineBlock {
    start_time: datetime
    end_time: datetime
    file_path: str
    file_size: int
    duration: int
    has_gaps: bool
}

CameraTimeline {
    camera_id: int
    blocks: List[TimelineBlock]
    total_duration: int
    coverage_percent: float
    last_updated: datetime
}
```

### 2. Django App (Timeline)

**Responsabilidades:**
- Configuração de retenção por câmera
- Auditoria de operações de storage
- API pública para frontend
- Interface administrativa
- Cleanup automático via Celery

**Models:**
```python
RetentionPlan {
    name: str
    days: int
    description: str
    is_active: bool
}

CameraRetention {
    camera: ForeignKey(Camera)
    retention_plan: ForeignKey(RetentionPlan)
    custom_days: int (nullable)
    enabled: bool
}

StorageAudit {
    camera: ForeignKey(Camera)
    action: str  # created, deleted, expired
    file_path: str
    file_size: int
    timestamp: datetime
}
```

## Fluxo de Dados

### 1. Indexação de Gravações
```
1. FastAPI escaneia /recordings/{camera_id}/
2. Para cada arquivo .mp4:
   - Extrai metadados com ffprobe
   - Calcula timestamp do filename
   - Adiciona ao índice em memória
3. Gera blocos contíguos de gravação
4. Cache resultado por TTL configurável
```

### 2. Timeline Request
```
1. Frontend → Django API
2. Django → FastAPI Service
3. FastAPI consulta cache ou reindexa
4. Retorna blocos de timeline
5. Frontend renderiza timeline visual
```

### 3. Video Playback
```
1. User clica na timeline (timestamp)
2. Frontend → FastAPI /video/{camera_id}/{timestamp}
3. FastAPI resolve timestamp para arquivo correto
4. Retorna URL ou redirect para arquivo
5. Player carrega vídeo no timestamp exato
```

### 4. Retention Cleanup
```
1. Celery task executa diariamente
2. Para cada câmera:
   - Consulta configuração de retenção
   - Calcula data de expiração
   - Lista arquivos expirados
   - Deleta arquivos em batches
   - Log auditoria no Django
3. Notifica FastAPI para invalidar cache
```

## Estrutura de Arquivos

### Recordings Directory
```
/recordings/
├── cam_1/
│   ├── 2024-01-15/
│   │   ├── 00-00-00.mp4  # 00:00:00
│   │   ├── 00-05-00.mp4  # 00:05:00
│   │   └── ...
│   └── 2024-01-16/
└── cam_2/
    └── ...
```

### Service Directory
```
services/timeline/
├── main.py              # FastAPI app
├── models.py            # Pydantic models
├── indexer.py           # File indexing logic
├── cache.py             # Memory cache
├── filesystem.py        # File utilities
├── config.py            # Configuration
├── Dockerfile
└── requirements.txt
```

### Django App Directory
```
backend/apps/timeline/
├── models.py            # Django models
├── serializers.py       # DRF serializers
├── views.py             # API views
├── services.py          # Business logic
├── tasks.py             # Celery tasks
├── admin.py             # Admin interface
└── urls.py              # URL routing
```

## Performance Considerations

### Caching Strategy
- **Memory Cache**: Índices de timeline (TTL: 5 min)
- **Redis Cache**: Metadados de vídeo (TTL: 1 hora)
- **Database Cache**: Configurações de retenção

### Optimization Techniques
- **Lazy Loading**: Metadados carregados sob demanda
- **Batch Processing**: Cleanup em lotes de 100 arquivos
- **Async Operations**: Todas as operações I/O assíncronas
- **Index Partitioning**: Índices separados por câmera/data

### Scalability Limits
- **Files per Camera**: 10,000 arquivos/dia
- **Concurrent Cameras**: 100+ câmeras
- **Timeline Response**: < 2 segundos
- **Indexing Speed**: 1000 arquivos/30 segundos

## Security & Compliance

### Access Control
- Django permissions para configuração
- FastAPI sem autenticação (interno)
- File system permissions restritivas

### Audit Trail
- Todas as operações de cleanup logadas
- Rastreabilidade completa de deletions
- Backup de configurações críticas

### Data Protection
- Validação antes de deletar arquivos
- Rollback em caso de erro
- Preservação de arquivos com detecções

## Monitoring & Alertas

### Métricas Chave
- Timeline response time
- Cache hit rate
- Indexing duration
- Cleanup efficiency
- Disk usage per camera

### Alertas Críticos
- Disk space < 10%
- Indexing failures
- Cleanup errors
- Service unavailability

## Deployment

### Docker Compose
```yaml
timeline-service:
  build: ./services/timeline
  ports:
    - "8007:8007"
  volumes:
    - ./recordings:/recordings:ro
  environment:
    - RECORDINGS_PATH=/recordings
    - CACHE_TTL=300
```

### Environment Variables
```bash
# FastAPI Service
RECORDINGS_PATH=/recordings
CACHE_TTL=300
MAX_SCAN_DEPTH=3
DJANGO_API_URL=http://django:8000

# Django App
TIMELINE_SERVICE_URL=http://timeline:8007
CLEANUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
MIN_FREE_SPACE_GB=50
```