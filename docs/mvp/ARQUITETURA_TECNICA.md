# 🎯 ARQUITETURA TÉCNICA - GRAVAÇÃO 24/7

## DECISÕES TÉCNICAS FUNDAMENTAIS

### 1. Por que fMP4 (Fragmented MP4)?

**Alternativas consideradas**:
- ❌ **TS (MPEG-TS)**: Overhead alto (~10%), difícil de indexar
- ❌ **MKV**: Não nativo no MediaMTX, problemas com HLS
- ✅ **fMP4**: Padrão moderno, baixo overhead, compatível HLS/DASH

**Vantagens do fMP4**:
```
┌─────────────────────────────────────┐
│ Arquivo fMP4                        │
├─────────────────────────────────────┤
│ [ftyp] - File Type Box              │
│ [moov] - Movie Header (metadata)    │
│ [moof] - Movie Fragment 1           │
│ [mdat] - Media Data 1               │
│ [moof] - Movie Fragment 2           │
│ [mdat] - Media Data 2               │
│ ...                                 │
└─────────────────────────────────────┘
```

- Headers distribuídos (recuperável se corrompido)
- Escrita incremental (sem reescrever arquivo)
- Seek rápido (índice em cada fragmento)
- Compatível com HLS nativo

### 2. Por que 1 hora por arquivo?

**Análise de trade-offs**:

| Duração | Prós | Contras |
|---------|------|---------|
| 5 min | Granularidade fina | 288 arquivos/dia, overhead de I/O |
| 15 min | Boa granularidade | 96 arquivos/dia |
| **1 hora** | **Padrão VMS, 24 arquivos/dia** | **Seek pode ser lento** |
| 24 horas | 1 arquivo/dia | Arquivo muito grande (>20GB) |

**Decisão**: 1 hora é o padrão da indústria (Milestone, Genetec, Nx Witness).

### 3. Por que NÃO gravar HLS?

HLS é um formato de **streaming**, não de **armazenamento**:

```
HLS (Live):
cam_1/
├── index.m3u8
├── segment_001.ts (4s)
├── segment_002.ts (4s)
├── segment_003.ts (4s)
└── ... (apagados após 24s)
```

**Problemas**:
- ❌ Segmentos pequenos (4s) = milhares de arquivos
- ❌ Overhead de I/O absurdo
- ❌ Difícil de indexar
- ❌ Não é padrão para storage

**Solução**: Gravar MP4, servir HLS sob demanda.

---

## FLUXO DE GRAVAÇÃO DETALHADO

### Passo a Passo

```
1. Câmera conecta via RTSP
   rtsp://192.168.1.100:554/stream1
   
2. MediaMTX recebe stream
   - Decodifica RTP packets
   - Extrai H.264 + AAC
   
3. MediaMTX grava em fMP4
   - Fragmentos de 2s (recordPartDuration)
   - Acumula até 1h (recordSegmentDuration)
   - Salva em /recordings/cam_1/2026-02-05/15.mp4
   
4. Após 1 hora
   - Fecha arquivo 15.mp4
   - Inicia novo arquivo 16.mp4
   
5. Após 7 dias (168h)
   - MediaMTX apaga automaticamente
   - /recordings/cam_1/2026-01-29/ é deletado
```

### Código Interno do MediaMTX (Simplificado)

```go
// MediaMTX internal (não precisa implementar)
func (r *Recorder) Run() {
    for {
        packet := <-r.stream
        
        // Escreve fragmento
        r.currentFragment.Write(packet)
        
        // Verifica se completou 1 hora
        if time.Since(r.segmentStart) >= r.segmentDuration {
            r.closeSegment()
            r.openNewSegment()
        }
        
        // Verifica retenção
        r.deleteOldSegments()
    }
}
```

---

## ESTRUTURA DE DADOS

### Hierarquia de Diretórios

```
/recordings/
├── cam_1/                    # Camera ID
│   ├── 2026-02-05/           # Date (YYYY-MM-DD)
│   │   ├── 00.mp4            # Hour 00 (00:00-00:59)
│   │   ├── 01.mp4            # Hour 01 (01:00-01:59)
│   │   ├── ...
│   │   └── 23.mp4            # Hour 23 (23:00-23:59)
│   ├── 2026-02-06/
│   │   └── ...
│   └── 2026-02-07/
│       └── ...
├── cam_2/
│   └── ...
```

### Nomenclatura de Arquivos

**Padrão**: `{HH}.mp4`

**Exemplos**:
- `00.mp4` → 00:00:00 até 00:59:59
- `15.mp4` → 15:00:00 até 15:59:59
- `23.mp4` → 23:00:00 até 23:59:59

**Por que não incluir minutos/segundos?**
- Arquivos sempre começam em hora cheia
- Simplifica busca (1 arquivo por hora)
- Padrão da indústria

### Metadados do Arquivo

Cada arquivo MP4 contém:

```
[moov] Movie Header
├── [mvhd] Movie Header Box
│   ├── creation_time: 2026-02-05T15:00:00Z
│   ├── duration: 3600s
│   └── timescale: 90000
├── [trak] Video Track
│   ├── codec: H.264
│   ├── resolution: 1920×1080
│   ├── fps: 25
│   └── bitrate: 3000 kbps
└── [trak] Audio Track
    ├── codec: AAC
    ├── sample_rate: 48000 Hz
    └── bitrate: 128 kbps
```

---

## PLAYBACK: ARQUITETURA DETALHADA

### Problema

Player consome HLS, mas gravações são MP4.

### Solução: MediaMTX como Transcoder On-Demand

```
┌─────────┐
│ Player  │
└────┬────┘
     │ GET /hls/playback_cam_1_1738771800/index.m3u8
     ▼
┌─────────────┐
│  Backend    │
│  (FastAPI)  │
└─────┬───────┘
      │ 1. Identifica arquivo: /recordings/cam_1/2026-02-05/15.mp4
      │ 2. Cria path temporário no MediaMTX
      ▼
┌──────────────┐
│  MediaMTX    │
│  Playback    │
└──────┬───────┘
       │ 3. Lê MP4
       │ 4. Remux para HLS (sem reencodar)
       ▼
┌──────────────┐
│  HLS Stream  │
│  (temporário)│
└──────────────┘
       │
       ▼
┌─────────┐
│ Player  │ (não sabe que é gravação)
└─────────┘
```

### API de Playback

#### 1. Buscar Timeline

```http
GET /api/playback/timeline?camera_id=1&date=2026-02-05

Response:
{
  "segments": [
    {
      "start": "2026-02-05T00:00:00Z",
      "end": "2026-02-05T00:59:59Z",
      "file": "/recordings/cam_1/2026-02-05/00.mp4",
      "size_bytes": 1350000000
    },
    {
      "start": "2026-02-05T01:00:00Z",
      "end": "2026-02-05T01:59:59Z",
      "file": "/recordings/cam_1/2026-02-05/01.mp4",
      "size_bytes": 1350000000
    },
    ...
  ]
}
```

#### 2. Iniciar Playback

```http
POST /api/playback/start
{
  "camera_id": 1,
  "start_time": "2026-02-05T15:30:00Z"
}

Response:
{
  "success": true,
  "hls_url": "/hls/playback_cam_1_1738771800/index.m3u8",
  "playback_id": "playback_cam_1_1738771800"
}
```

#### 3. Player Consome HLS

```javascript
// Frontend (não muda)
const player = new Hls();
player.loadSource('/hls/playback_cam_1_1738771800/index.m3u8');
player.attachMedia(videoElement);
```

### MediaMTX Playback API (Interno)

```http
POST http://mediamtx:9997/v3/config/paths/add/playback_cam_1_1738771800
Authorization: Basic mediamtx_api_user:GtV!sionMed1aMTX$2025

{
  "source": "file:///recordings/cam_1/2026-02-05/15.mp4",
  "sourceOnDemand": true,
  "record": false
}
```

MediaMTX automaticamente:
1. Lê o arquivo MP4
2. Demux H.264 + AAC
3. Remux para HLS (fMP4)
4. Serve em `/hls/playback_cam_1_1738771800/`

---

## ESCALA: ARQUITETURA MULTI-NÓ

### Problema

1 MediaMTX suporta ~12 câmeras. MVP precisa de 120.

### Solução: 10 Nós MediaMTX

```
┌──────────────────────────────────────────────┐
│           Backend (Django/FastAPI)           │
│         Orquestrador de Nós                  │
└───────┬──────────────────────────────────────┘
        │
        ├─────────┬─────────┬─────────┬─────────┐
        ▼         ▼         ▼         ▼         ▼
    ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
    │MediaMTX││MediaMTX││MediaMTX││MediaMTX││MediaMTX│
    │ Nó 1   ││ Nó 2   ││ Nó 3   ││ Nó 4   ││ Nó 5   │
    │12 cams ││12 cams ││12 cams ││12 cams ││12 cams │
    └────────┘└────────┘└────────┘└────────┘└────────┘
    
    ┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
    │MediaMTX││MediaMTX││MediaMTX││MediaMTX││MediaMTX│
    │ Nó 6   ││ Nó 7   ││ Nó 8   ││ Nó 9   ││ Nó 10  │
    │12 cams ││12 cams ││12 cams ││12 cams ││12 cams │
    └────────┘└────────┘└────────┘└────────┘└────────┘
```

### Tabela de Alocação (Backend)

```sql
CREATE TABLE media_nodes (
    id SERIAL PRIMARY KEY,
    hostname VARCHAR(255),
    api_url VARCHAR(255),
    hls_url VARCHAR(255),
    max_cameras INT DEFAULT 12,
    current_cameras INT DEFAULT 0,
    status VARCHAR(50), -- 'active', 'degraded', 'offline'
    disk_usage_percent FLOAT,
    cpu_usage_percent FLOAT,
    last_health_check TIMESTAMP
);

CREATE TABLE camera_node_mapping (
    camera_id INT PRIMARY KEY,
    node_id INT REFERENCES media_nodes(id),
    assigned_at TIMESTAMP
);
```

### Algoritmo de Alocação

```python
def allocate_camera(camera_id: int) -> int:
    """Aloca câmera no nó com menor carga."""
    nodes = MediaNode.objects.filter(
        status='active',
        current_cameras__lt=F('max_cameras')
    ).order_by('current_cameras')
    
    if not nodes:
        raise Exception("No available nodes")
    
    node = nodes.first()
    node.current_cameras += 1
    node.save()
    
    CameraNodeMapping.objects.create(
        camera_id=camera_id,
        node_id=node.id
    )
    
    return node.id
```

---

## MONITORAMENTO E OBSERVABILIDADE

### Métricas Críticas

```yaml
Gravação:
  - recording_active: bool
  - recording_duration_seconds: gauge
  - recording_file_size_bytes: gauge
  - recording_errors_total: counter

Disco:
  - disk_usage_percent: gauge
  - disk_free_bytes: gauge
  - oldest_recording_age_hours: gauge

Performance:
  - cpu_usage_percent: gauge
  - memory_usage_bytes: gauge
  - network_rx_bytes_total: counter
  - network_tx_bytes_total: counter
```

### Alertas

```yaml
- alert: DiskAlmostFull
  expr: disk_usage_percent > 80
  for: 5m
  severity: warning

- alert: DiskFull
  expr: disk_usage_percent > 95
  for: 1m
  severity: critical

- alert: RecordingFailed
  expr: recording_active == 0
  for: 5m
  severity: critical

- alert: CameraOffline
  expr: camera_connected == 0
  for: 5m
  severity: warning
```

---

## DEPLOY: LOCAL vs CLOUD

### Local (On-Prem)

```yaml
# docker-compose.yml
mediamtx:
  image: bluenviron/mediamtx:latest-ffmpeg
  volumes:
    - /mnt/ssd/recordings:/recordings  # SSD local
  deploy:
    resources:
      limits:
        cpus: '2.5'
        memory: 2G
```

**Disco**: SSD NVMe 4TB (~$400)

### Cloud (AWS)

```hcl
# terraform/mediamtx_node.tf
resource "aws_instance" "mediamtx_node" {
  count         = 10
  ami           = "ami-0c55b159cbfafe1f0"  # Ubuntu 22.04
  instance_type = "t3.large"  # 2 vCPU, 8GB RAM
  
  ebs_block_device {
    device_name = "/dev/sdf"
    volume_type = "gp3"
    volume_size = 3000  # 3TB
    iops        = 3000
    throughput  = 125
  }
}
```

**Custo**: ~$316/mês por nó (EC2 + EBS)

---

## BACKUP E DISASTER RECOVERY

### Estratégia de Backup

```
Tier 1 (Hot): EBS local (7 dias)
Tier 2 (Warm): S3 Standard (30 dias)
Tier 3 (Cold): S3 Glacier (1 ano)
```

### Sincronização para S3

```bash
# Cron diário (00:00)
aws s3 sync /recordings/ s3://gtvision-recordings/ \
  --exclude "*" \
  --include "*/$(date -d '1 day ago' +%Y-%m-%d)/*" \
  --storage-class STANDARD
```

### Recovery

```bash
# Restaurar dia específico
aws s3 sync s3://gtvision-recordings/cam_1/2026-02-05/ \
  /recordings/cam_1/2026-02-05/
```

---

## PERFORMANCE: BENCHMARKS

### Disco (SSD NVMe)

```
Write: 3000 MB/s
Read: 3500 MB/s
IOPS: 500k

12 câmeras × 3 Mbps = 36 Mbps = 4.5 MB/s
Utilização: 0.15% (sobra muito)
```

### CPU

```
1 câmera gravando: ~5% CPU
12 câmeras: ~60% CPU
Limite: 2.5 cores = 250% CPU
Margem: 190% disponível
```

### Rede

```
12 câmeras × 3 Mbps = 36 Mbps
Gigabit Ethernet: 1000 Mbps
Utilização: 3.6%
```

**Conclusão**: Gargalo é CPU, não disco ou rede.
