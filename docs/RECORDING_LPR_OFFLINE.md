# 🎬 Sistema de Gravação e LPR Offline

## 📋 Fluxo Completo

### 1. Streaming On-Demand (Não Mexemos)
```
RTSP → MediaMTX → HLS On-Demand
```
- Streaming só inicia quando player é aberto
- Economia de banda e CPU

### 2. Gravação Automática
```
HLS Iniciado → MediaMTX grava automaticamente → /recordings/cam_X/YYYY-MM-DD/HH-MM-SS.mp4
```
- Gravação inicia quando HLS é acessado
- Para quando HLS fecha (após 30s sem viewers)
- Retenção: 7 dias (168h)

### 3. Snapshot em Cache
```
Gravação Finalizada → Task Celery → Extrai 1º frame → Salva em /media/recording_snapshots/
```
- Thumbnail 320x180 JPEG otimizado
- Cache permanente no banco (ImageField)
- Lista de gravações não gera banda desnecessária

### 4. LPR Offline (Não Tempo Real)
```
Gravação Finalizada → Worker LPR → Processa vídeo → Salva detecções
```
- Processa 1 frame a cada 2 segundos
- YOLO + EasyOCR
- Salva snapshots de placas detectadas

## 🗂️ Estrutura de Arquivos

```
/recordings/
  cam_1/
    2025-01-15/
      10-30-00-000.mp4  (1 hora)
      11-30-00-000.mp4
  cam_2/
    2025-01-15/
      ...

/media/
  recording_snapshots/
    2025/01/15/
      rec_1_20250115_103000.jpg  (thumbnail cache)
      rec_2_20250115_110000.jpg
  snapshots/
    2025/01/15/
      1_1500_ABC1234.jpg  (detecção LPR)
```

## 🚀 Como Usar

### Backend - Listar Gravações
```python
GET /api/recordings?camera_id=1&limit=50

Response:
[
  {
    "id": 1,
    "camera_id": 1,
    "camera_name": "Entrada Principal",
    "video_path": "/recordings/cam_1/2025-01-15/10-30-00.mp4",
    "snapshot_url": "/media/recording_snapshots/2025/01/15/rec_1.jpg",  # CACHE
    "duration_seconds": 3600,
    "file_size_mb": 450.5,
    "started_at": "2025-01-15T10:30:00Z",
    "ended_at": "2025-01-15T11:30:00Z",
    "lpr_processed": true,
    "lpr_detections_count": 15
  }
]
```

### Frontend - Exibir Lista
```jsx
<RecordingCard>
  <img src={recording.snapshot_url} />  {/* Foto estática em cache */}
  <p>{recording.camera_name}</p>
  <p>{recording.duration_seconds}s</p>
  <Badge>{recording.lpr_detections_count} placas</Badge>
</RecordingCard>
```

## ⚙️ Configuração

### MediaMTX (mediamtx.yml)
```yaml
pathDefaults:
  sourceOnDemand: yes
  sourceOnDemandCloseAfter: 30s
  record: yes
  recordPath: /recordings/%path/%Y-%m-%d/%H-%M-%S-%f
  recordSegmentDuration: 1h
  recordDeleteAfter: 168h  # 7 dias
```

### Docker Compose
```yaml
lpr_offline:
  image: gtvision/lpr:latest
  command: python lpr_recording_processor.py
  volumes:
    - mediamtx_recordings:/recordings:ro
```

### Celery Tasks
```python
# Gera snapshot após gravação finalizar
generate_recording_snapshot.delay(recording_id)

# Processa LPR offline
process_recording_lpr.delay(recording_id)
```

## 📊 Vantagens

✅ **Economia de Banda**: Thumbnails em cache, não streaming contínuo  
✅ **Economia de CPU**: LPR processa offline, não em tempo real  
✅ **Escalável**: Worker LPR pode processar múltiplas gravações em paralelo  
✅ **Confiável**: Gravações persistidas, não dependem de streaming ativo  
✅ **UX Melhor**: Lista de gravações carrega instantaneamente (cache)

## 🔧 Manutenção

### Limpar gravações antigas
```bash
# MediaMTX faz automaticamente após 7 dias
# Ou manual:
find /recordings -type f -mtime +7 -delete
```

### Reprocessar LPR
```python
Recording.objects.filter(lpr_processed=False).update(lpr_processed=False)
# Worker vai reprocessar automaticamente
```
