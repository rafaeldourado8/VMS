# PASSO 7 - Gravação Cíclica

## Objetivo
Implementar sistema de gravação automática com limpeza cíclica, seguindo arquitetura DDD e 3 regras de ouro para integração com MediaMTX.

## Arquitetura

### 3 Regras de Ouro
1. ✅ **Backend NUNCA cria path no MediaMTX** - Paths são criados automaticamente quando câmeras conectam
2. ✅ **Backend NUNCA considera path not found como erro** - É estado normal (câmera offline)
3. ✅ **path not found = câmera OFFLINE** - Não é falha, é informação de estado

### Domínio Recording
**Arquivos:**
- `src/shared/streaming/recording/models.py` - RecordingSession, RecordingStatus
- `src/shared/streaming/recording/recording_manager.py` - Interface RecordingManager

**Entidades:**
```python
@dataclass
class RecordingSession:
    camera_id: UUID
    stream_id: str
    status: RecordingStatus  # ON | OFF
    started_at: datetime
    storage_path: str
    city_id: UUID
```

### Ports & Adapters
**Arquivos:**
- `src/shared/streaming/core/ports.py` - RecordingPort (contrato)
- `src/infrastructure/adapters/recording/mock_recording_adapter.py` - Mock para testes
- `src/infrastructure/adapters/recording/mediamtx_recording_adapter.py` - Adapter real

**MediaMTXRecordingAdapter:**
```python
class MediaMTXRecordingAdapter:
    def start(self, stream_id: str) -> None:
        # MediaMTX já grava automaticamente (record: yes global)
        pass
    
    def stop(self, stream_id: str) -> None:
        # MediaMTX para automaticamente quando fonte desconecta
        pass
    
    def status(self, stream_id: str) -> Optional[RecordingStatus]:
        # Verifica se path existe (ONLINE) ou não (OFFLINE)
        path_info = self.mediamtx.get_path(stream_id)
        return RecordingStatus.ON if path_info else None
```

### Manager
**Arquivo:** `src/infrastructure/cache/streaming/redis_recording_manager.py`

**RedisRecordingManager:**
- Implementa RecordingManager
- Salva sessões no Redis (TTL 24h)
- Atualiza `camera.recording_enabled` no banco
- MediaMTX gerencia gravação automaticamente

### Path Observer
**Arquivo:** `src/infrastructure/observers/path_observer.py`

**PathObserver:**
- Monitora `/v3/paths/list` a cada 10 segundos
- Detecta paths criados (câmera ONLINE)
- Detecta paths removidos (câmera OFFLINE)
- Callbacks para lógica de negócio

```python
class PathObserver:
    async def _sync_paths(self):
        # Consulta paths ativos no MediaMTX
        current_paths = {item['name'] for item in response.get('items', [])}
        
        # Detecta novos paths
        new_paths = current_paths - self.known_paths
        for path_name in new_paths:
            await self._on_path_created(path_name)
        
        # Detecta paths removidos
        removed_paths = self.known_paths - current_paths
        for path_name in removed_paths:
            await self._on_path_removed(path_name)
```

### API Endpoints
**Arquivo:** `src/shared/streaming/stream/api.py`

**Recording:**
- `PUT /api/v1/cameras/{camera_id}/recording` - Habilitar gravação
- `DELETE /api/v1/cameras/{camera_id}/recording` - Desabilitar gravação
- `GET /api/v1/cameras/{camera_id}/recording` - Status gravação

**Response Models:**
```python
class RecordingEnableResponse(BaseModel):
    camera_id: UUID
    recording: bool = True
    storage_path: str
    enabled_at: datetime

class RecordingStatusResponse(BaseModel):
    camera_id: UUID
    recording: bool
    storage_path: Optional[str]
    started_at: Optional[datetime]
```

## Configuração MediaMTX

**Arquivo:** `src/infrastructure/servers/mediamtx.yml`

```yaml
pathDefaults:
  record: yes  # Gravação global habilitada
  recordPath: /recordings/%path/%Y-%m-%d_%H-%M-%S-%f
  recordFormat: fmp4
  recordPartDuration: 4s
  recordSegmentDuration: 30m  # Segmentos de 30 minutos
  recordDeleteAfter: 7d  # Limpeza cíclica após 7 dias
```

**Volume Docker:**
```yaml
mediamtx:
  volumes:
    - ./recordings:/recordings
```

## Fluxo de Gravação

### 1. Habilitar Gravação
```
Cliente → PUT /api/v1/cameras/{id}/recording
    ↓
RedisRecordingManager.enable_recording()
    ↓
camera.recording_enabled = True (banco)
    ↓
RecordingSession salva no Redis (TTL 24h)
    ↓
MediaMTX grava automaticamente quando câmera conectar
```

### 2. Câmera Conecta
```
Câmera conecta → MediaMTX cria path automaticamente
    ↓
PathObserver detecta path criado (10s)
    ↓
Callback _on_path_created(path_name)
    ↓
MediaMTX inicia gravação (record: yes global)
    ↓
Arquivos salvos em /recordings/{path}/
```

### 3. Gravação Ativa
```
MediaMTX grava continuamente
    ↓
Segmentos de 30 minutos
    ↓
Formato fmp4 (low-latency)
    ↓
Limpeza automática após 7 dias
```

### 4. Câmera Desconecta
```
Câmera desconecta → MediaMTX remove path automaticamente
    ↓
PathObserver detecta path removido (10s)
    ↓
Callback _on_path_removed(path_name)
    ↓
MediaMTX para gravação automaticamente
```

## Estrutura de Arquivos

```
/recordings/
  stream_{camera_id}/
    2026-01-27_03-00-00-123456.mp4
    2026-01-27_03-30-00-789012.mp4
    2026-01-27_04-00-00-345678.mp4
```

## Isolamento Multi-Tenant

- Headers obrigatórios: `X-City-ID`, `X-User-ID`
- RecordingSession isolado por `city_id`
- Redis keys: `recording:{camera_id}`
- Validação de acesso em todos os endpoints

## Testes

### Scripts
- `scripts/test_recording_mock.bat` - Teste com MockAdapter
- `scripts/test_passo7_final.bat` - Teste completo
- `scripts/test_path_observer.bat` - Teste PathObserver

### Teste Manual
```bash
# 1. Habilitar gravação
curl -X PUT http://localhost:8001/api/v1/cameras/{id}/recording \
  -H "X-City-ID: {city_id}" \
  -H "X-User-ID: 1"

# 2. Iniciar stream
curl -X POST "http://localhost:8001/api/v1/streams?camera_id={id}" \
  -H "X-City-ID: {city_id}" \
  -H "X-User-ID: 1"

# 3. Aguardar 35 segundos

# 4. Verificar arquivos
dir recordings\stream_{camera_id}
```

## Melhorias Implementadas

### Contratos de API
- Versionamento `/api/v1/`
- Response models Pydantic
- Tags organizadas (Streaming, Recording, Mosaics, System)
- Documentação OpenAPI em `/docs`
- HTTP status codes corretos

### Health Check
```python
@app.get("/health", response_model=HealthResponse)
async def health():
    mediamtx_ok = mediamtx.get_all_paths() is not None
    redis_ok = redis_client.ping()
    
    return HealthResponse(
        status="healthy" if (mediamtx_ok and redis_ok) else "degraded",
        mediamtx=mediamtx_ok,
        redis=redis_ok
    )
```

## Próximos Passos

### Passo 8 - Player de Replay
- Listar gravações por câmera/período
- Player HLS para gravações
- Timeline de navegação

### Passo 9 - Busca e Download
- Busca por horário/data
- Download de segmentos
- Exportação forense

### Passo 10 - Eventos e IA
- Detecção de movimento
- LPR (reconhecimento de placas)
- Alertas em tempo real

## Referências

- MediaMTX API v3: https://github.com/bluenviron/mediamtx
- FastAPI: https://fastapi.tiangolo.com/
- Pydantic: https://docs.pydantic.dev/
