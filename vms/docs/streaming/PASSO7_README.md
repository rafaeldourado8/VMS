# PASSO 7 - Gravação Cíclica

## Objetivo
Garantir que o sistema consiga gravar streams de forma cíclica, sobrescrevendo automaticamente quando atingir limite de espaço/tempo.

## Escopo

### ✅ O que ENTRA
- Gravar streams em disco
- Sobrescrever gravações antigas automaticamente
- Limpeza cíclica por tempo/espaço
- Sobreviver a restarts
- Configuração por câmera (habilitar/desabilitar)

### ❌ O que NÃO ENTRA (Passo 8+)
- Player de replay
- Busca por horário
- Download de gravações
- Eventos LPR
- IA / Motion detection
- Interface UI

## Arquitetura

### Estratégia
Usar MediaMTX recording nativo com configuração dinâmica via API.

### Configuração MediaMTX
```yaml
pathDefaults:
  record: no  # Desabilitado por padrão
  recordPath: /recordings/%path/%Y-%m-%d_%H-%M-%S-%f
  recordFormat: fmp4
  recordPartDuration: 4s
  recordSegmentDuration: 30m  # Segmentos de 30 minutos
  recordDeleteAfter: 7d  # Limpa após 7 dias
```

### Paths Dinâmicos
Quando stream inicia com recording habilitado:
```yaml
paths:
  stream_{camera_id}:
    source: rtsp://...
    record: yes
    recordPath: /recordings/{city_id}/{camera_id}/%Y-%m-%d_%H-%M-%S
    recordDeleteAfter: 7d
```

## Implementação

### 1. Model Camera
Adicionar campo `recording_enabled` (boolean, default False).

### 2. RecordingManager Interface
```python
class RecordingManager(ABC):
    @abstractmethod
    async def enable_recording(self, camera_id: UUID, city_id: UUID) -> bool
    
    @abstractmethod
    async def disable_recording(self, camera_id: UUID, city_id: UUID) -> bool
    
    @abstractmethod
    async def get_recording_status(self, camera_id: UUID, city_id: UUID) -> dict
```

### 3. MediaMTXRecordingManager
Implementação que usa HTTPMediaMTXAdapter para:
- Atualizar path config via API
- Habilitar/desabilitar recording
- Verificar status

### 4. Endpoints FastAPI
```
POST   /api/recording/enable/{camera_id}
POST   /api/recording/disable/{camera_id}
GET    /api/recording/status/{camera_id}
```

### 5. Volume Docker
Montar `/recordings` persistente no MediaMTX.

## Fluxo

### Habilitar Gravação
1. Cliente: POST /api/recording/enable/{camera_id}
2. RecordingManager valida camera existe e está ativa
3. Atualiza Camera.recording_enabled = True no DB
4. Atualiza path config no MediaMTX via API
5. MediaMTX inicia gravação automaticamente

### Desabilitar Gravação
1. Cliente: POST /api/recording/disable/{camera_id}
2. RecordingManager valida camera
3. Atualiza Camera.recording_enabled = False no DB
4. Atualiza path config no MediaMTX via API
5. MediaMTX para gravação

### Limpeza Automática
MediaMTX gerencia automaticamente via `recordDeleteAfter: 7d`.

## Testes

### Script test_recording.bat
```batch
# Habilitar gravação
curl -X POST /api/recording/enable/{camera_id}

# Verificar status
curl /api/recording/status/{camera_id}

# Aguardar 1 minuto

# Verificar arquivos no volume
docker exec mediamtx ls /recordings/{city_id}/{camera_id}/

# Desabilitar gravação
curl -X POST /api/recording/disable/{camera_id}
```

## Estrutura de Arquivos
```
/recordings/
  {city_id}/
    {camera_id}/
      2026-01-27_03-00-00.mp4
      2026-01-27_03-30-00.mp4
      2026-01-27_04-00-00.mp4
```

## Configuração

### Docker Compose
```yaml
mediamtx:
  volumes:
    - ./recordings:/recordings
```

### Settings
```python
RECORDING_SEGMENT_DURATION = 30  # minutos
RECORDING_DELETE_AFTER_DAYS = 7
RECORDING_MAX_SIZE_GB = 100  # por câmera
```

## Próximos Passos
- Passo 8: Player de replay
- Passo 9: Busca por horário
- Passo 10: Download de gravações
