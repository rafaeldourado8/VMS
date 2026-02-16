# Arquitetura de Gravações - VMS

## Visão Geral

O sistema de gravações do VMS é composto por 4 componentes principais que trabalham em conjunto:

```
┌─────────────────┐
│  Recorder       │ Grava vídeos RTSP em segmentos de 1min
│  (porta 8002)   │ Salva em: /recordings/camera_{id}/{date}/{HH-MM-SS}.mp4
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Storage        │ Indexa gravações no PostgreSQL
│  (porta 8003)   │ API: /timeline/{camera_id}?date=YYYY-MM-DD
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Cleanup        │ Remove gravações ao fim do período de retenção
│  (retention)    │ Executa a cada 1 hora | Planos: 7, 15, 30 dias
└─────────────────┘

┌─────────────────┐
│  Backend Django │ App recordings (opcional)
│  (porta 8000)   │ Modelo Recording para metadados
└─────────────────┘
```


**Arquivo**: `services/recorder/recorder.py`

### Responsabilidades:
- Conecta em câmeras RTSP via FFmpeg
- Grava vídeos em segmentos de 60 segundos
- Organiza arquivos por câmera e data
- Monitora e reinicia processos que falham

### Estrutura de Arquivos:
```
/recordings/
  camera_12/
    2025-02-16/
      15-13-43.mp4  (1 minuto)
      15-14-43.mp4  (1 minuto)
      15-15-43.mp4  (1 minuto)
```

### Comando FFmpeg:
```bash
ffmpeg -rtsp_transport tcp -i {rtsp_url} \
  -c:v copy -c:a copy \
  -f segment -segment_time 60 \
  -segment_format mp4 \
  -reset_timestamps 1 \
  -strftime 1 \
  /recordings/camera_{id}/{date}/%H-%M-%S.mp4
```

### Sincronização:
- Busca câmeras ativas do backend a cada 30 segundos
- Endpoint: `GET http://backend:8000/api/cameras/recorder/`
- Inicia/para gravações automaticamente

## 2. Storage Service

**Arquivo**: `services/storage/main.py`

### Responsabilidades:
- Escaneia diretório `/recordings` a cada 60 segundos
- Indexa segmentos no PostgreSQL (tabela `recording_segments`)
- Fornece API REST para consulta de gravações
- Serve arquivos MP4 via HTTP

### Banco de Dados:
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
CREATE INDEX idx_camera_time ON recording_segments(camera_id, start_time, end_time);
```

### API Endpoints:

#### GET /timeline/{camera_id}?date=YYYY-MM-DD
Retorna timeline de gravações para uma câmera em uma data específica.

**Resposta**:
```json
{
  "blocks": [
    {
      "start_time": "2025-02-16T15:13:43",
      "end_time": "2025-02-16T15:14:43",
      "duration_seconds": 60,
      "file_path": "http://localhost:8003/download/12/2025-02-16/15-13-43",
      "file_size_bytes": 5242880
    }
  ]
}
```

#### GET /download/{camera_id}/{date}/{filename}
Serve arquivo MP4 para playback.

**Exemplo**: `http://localhost:8003/download/12/2025-02-16/15-13-43`

#### POST /recordings/query
Query avançada com range de tempo.

**Request**:
```json
{
  "camera_id": 12,
  "start_time": "2025-02-16T15:00:00",
  "end_time": "2025-02-16T16:00:00"
}
```

**Resposta**:
```json
{
  "blocks": [...],
  "gaps": [
    {
      "start": "2025-02-16T15:20:00",
      "end": "2025-02-16T15:25:00",
      "duration_seconds": 300
    }
  ]
}
```

#### GET /recordings/available-dates/{camera_id}
Lista datas com pelo menos 5 minutos de gravação.

**Resposta**:
```json
{
  "dates": ["2025-02-16", "2025-02-15", "2025-02-14"]
}
```

#### GET /recordings/stats
Estatísticas gerais do storage.

**Resposta**:
```json
{
  "total_segments": 1440,
  "processed_segments": 720,
  "pending_segments": 720,
  "total_size_gb": 12.5
}
```

## 3. Retention Cleanup Service

**Arquivo**: `services/recorder/retention_cleanup.py`

### Responsabilidades:
- Remove gravações antigas baseado em política FIFO (First In, First Out)
- Executa a cada 1 hora
- Respeita configuração individual de cada câmera
- **Remove apenas ao fim do período de retenção**

### Política de Retenção (FIFO):

O cleanup **mantém** as gravações durante todo o período configurado e **deleta apenas** quando ultrapassam esse período.

**Planos disponíveis**:
- **7 dias**: Mantém últimos 7 dias completos, deleta gravações com 8+ dias
- **15 dias**: Mantém últimos 15 dias completos, deleta gravações com 16+ dias  
- **30 dias**: Mantém últimos 30 dias completos, deleta gravações com 31+ dias (padrão)

```python
# Exemplo: retention_days = 7
today = datetime.now().date()  # 2025-02-16
cutoff_date = today - timedelta(days=7)  # 2025-02-09

# Mantém: 2025-02-09 até 2025-02-16 (7 dias)
# Deleta: 2025-02-08 e anteriores
if folder_date < cutoff_date:
    shutil.rmtree(date_folder)
```

### Configuração por Câmera:
```json
{
  "id": 12,
  "recording_retention_days": 7  // Opções: 7, 15, 30 (padrão)
}
```

### Exemplo de Execução:
```
[INFO] Camera 12: Política 7 dias | Deletar antes de 2025-02-09
[INFO]   [DELETANDO] 2025-02-08: 1440 arquivos, 2048.00 MB
[INFO]   [DELETANDO] 2025-02-07: 1440 arquivos, 2048.00 MB
[INFO]   [OK] 2025-02-09 até 2025-02-16 mantidos (7 dias)
[INFO] TOTAL: 2880 arquivos deletados | 4096.00 MB liberados
```

## 4. Backend Django - App Recordings

**Diretório**: `backend/apps/recordings/`

### Modelo Recording:
```python
class Recording(models.Model):
    camera_id = models.IntegerField(db_index=True)
    date = models.DateField(db_index=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=512)
    size_mb = models.FloatField(default=0)
    duration_min = models.FloatField(default=0)
    codec = models.CharField(max_length=50, default='h264')
    is_valid = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['camera_id', 'date', 'file_name']
```

### Endpoints:
- `GET /api/recordings/` - Lista gravações
- `GET /api/recordings/by_camera/?camera_id=12&date=2025-02-16` - Por câmera
- `POST /api/recordings/sync_from_service/` - Sincroniza do Storage Service

**Nota**: O app Django é opcional. O Storage Service é a fonte primária de dados.

## Frontend - Integração

### API Service (api.ts)

```typescript
export const recordingService = {
  async list(params: { camera_id: number; date: string }) {
    const { data } = await axios.get(
      `http://localhost:8003/timeline/${params.camera_id}`,
      { params: { date: params.date } }
    )
    
    // Converte formato do Storage Service
    const recordings = data.blocks.map(block => ({
      camera_id: params.camera_id,
      date: params.date,
      filename: extractFilename(block.start_time),
      start_time: extractTime(block.start_time),
      duration_seconds: block.duration_seconds,
      file_size_bytes: block.file_size_bytes,
      url: block.file_path
    }))
    
    return { recordings, ... }
  },
  
  getPlaybackUrl(cameraId: number, date: string, filename: string): string {
    const timeStr = filename.replace('.mp4', '')
    return `http://localhost:8003/download/${cameraId}/${date}/${timeStr}`
  }
}
```

### Timeline Player Modal

```typescript
// Carrega gravações de hoje e ontem
const dates = [
  new Date().toISOString().split('T')[0],
  new Date(Date.now() - 86400000).toISOString().split('T')[0]
]

for (const date of dates) {
  const response = await recordingService.list({ camera_id, date })
  allRecordings.push(...response.recordings)
}

// Converte para blocos de timeline
const blocks = allRecordings.map(rec => ({
  start_time: `${rec.date}T${rec.start_time}`,
  end_time: calculateEndTime(rec),
  url: rec.url
}))
```

## Fluxo Completo

```
1. Câmera RTSP
   ↓
2. Recorder Service (FFmpeg)
   ↓ Grava segmentos de 1min
3. /recordings/camera_{id}/{date}/{HH-MM-SS}.mp4
   ↓
4. Storage Service (Scan a cada 60s)
   ↓ Indexa no PostgreSQL
5. recording_segments table
   ↓
6. Frontend (Timeline Player)
   ↓ GET /timeline/{camera_id}?date=...
7. Storage Service API
   ↓ Retorna {blocks: [...]}
8. Video Player
   ↓ GET /download/{camera_id}/{date}/{time}
9. Storage Service (FileResponse)
   ↓
10. Playback no navegador
```

## Troubleshooting

### Problema: Nenhuma gravação encontrada

**Verificações**:
1. Recorder está rodando? `docker ps | grep recorder`
2. Arquivos existem? `ls /recordings/camera_12/2025-02-16/`
3. Storage indexou? `curl http://localhost:8003/recordings/stats`
4. Data correta? Verificar timezone do sistema

### Problema: Vídeo não carrega

**Verificações**:
1. URL correta? `http://localhost:8003/download/{camera_id}/{date}/{time}`
2. Arquivo existe? Verificar path no filesystem
3. CORS configurado? Storage Service tem `allow_origins=["*"]`
4. Codec suportado? Verificar se é H.264

### Problema: Gravações antigas não são deletadas

**Verificações**:
1. Cleanup está rodando? `docker ps | grep cleanup`
2. Política configurada? Verificar `recording_retention_days` da câmera
3. Logs do cleanup: `docker logs vms-recorder-cleanup-1`

## Melhorias Futuras

1. **Compressão**: Comprimir gravações antigas (H.264 → H.265)
2. **Cloud Storage**: Upload para S3/Azure Blob
3. **Detecção de Movimento**: Marcar segmentos com movimento
4. **Thumbnails**: Gerar thumbnails para preview rápido
5. **Streaming Adaptativo**: HLS/DASH para melhor performance
6. **Busca por Evento**: Integrar com detecções LPR
7. **Export**: Exportar clips específicos
8. **Backup**: Backup automático de gravações importantes
