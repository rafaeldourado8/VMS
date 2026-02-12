# BUG-001: Gravações Duplicadas

**Data**: 2026-02-12  
**Severidade**: Alta  
**Status**: Resolvido ✅  
**Componentes**: recorder, streaming (MediaMTX)

---

## Descrição

O sistema estava gravando vídeos simultaneamente em dois diretórios diferentes, causando duplicação de armazenamento e inconsistência nos paths.

## Evidência

```
D:\VMS\recordings>tree /f
├───camera_1          ← Recorder (correto)
│   └───12_02_2026
│           12_39_04.mp4
│
└───cam_1             ← MediaMTX (duplicado)
    └───2026-02-12
            12-38-52-104075.mp4.mp4
```

## Causa Raiz

Dois serviços configurados para gravar simultaneamente:

1. **`services/recorder/recorder.py`**
   - Path: `/recordings/camera_{id}/{dd_mm_yyyy}/`
   - Segmentos: 1 minuto
   - Status: **Correto** ✅

2. **`services/streaming/main.py` (MediaMTX)**
   - Path: `/recordings/cam_{id}/{yyyy-mm-dd}/`
   - Config: `record: True` no provision
   - Status: **Duplicado** ❌

## Impacto

- ❌ Duplicação de espaço em disco
- ❌ Inconsistência de paths entre serviços
- ❌ Confusão sobre qual serviço usar
- ❌ Backend apontando para path errado (`cam_` vs `camera_`)

## Solução Implementada

### 1. Desabilitada gravação no MediaMTX

**Arquivo**: `services/streaming/main.py`

```python
# ANTES
config = {
    "record": True,
    "recordPath": "/recordings/%path/%Y-%m-%d/%H-%M-%S-%f.mp4",
    "recordFormat": "fmp4",
    ...
}

# DEPOIS
config = {
    "record": False
}
```

### 2. Mantido apenas recorder ativo

**Arquivo**: `docker-compose.yml`

```yaml
recorder:
  build:
    context: ./services/recorder
  volumes:
    - ./recordings:/recordings
  restart: unless-stopped
```

### 3. Criado script de limpeza

**Arquivo**: `scripts/cleanup_duplicate_recordings.bat`

Remove gravações duplicadas do MediaMTX (diretórios `cam_*`).

## Correções Adicionais Necessárias

### Backend - RecordingService

**Arquivo**: `backend/apps/recordings/services.py`

```python
# CORRIGIR DE:
recordings_path = Path(f"/recordings/cam_{camera_id}/{date}")

# PARA:
recordings_path = Path(f"/recordings/camera_{camera_id}/{date}")
```

### Recording Service API

**Arquivo**: `services/recording/main.py`

```python
# CORRIGIR DE:
base = Path(f"/recordings/cam_{camera_id}")

# PARA:
base = Path(f"/recordings/camera_{camera_id}")
```

## Comandos para Aplicar

```bash
# 1. Reconstruir streaming
docker-compose build streaming
docker-compose up -d streaming

# 2. Limpar duplicados
scripts\cleanup_duplicate_recordings.bat

# 3. Verificar
tree /f recordings
```

## Resultado Esperado

```
recordings/
└── camera_1/
    └── 12_02_2026/
        ├── 12_39_04.mp4
        ├── 12_40_04.mp4
        └── 12_41_04.mp4
```

## Prevenção

- [ ] Documentar claramente que **apenas recorder grava**
- [ ] MediaMTX apenas faz streaming (RTSP/HLS/WebRTC)
- [ ] Adicionar validação no CI/CD para verificar `record: False` no streaming
- [ ] Padronizar paths em todos os serviços: `camera_{id}`

## Referências

- `docs/FIX_DUPLICATE_RECORDINGS.md` - Documentação completa da correção
- `scripts/cleanup_duplicate_recordings.bat` - Script de limpeza
