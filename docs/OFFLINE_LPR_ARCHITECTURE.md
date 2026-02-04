# Arquitetura de Gravação Contínua + LPR Offline

## Visão Geral

Sistema VMS com gravação contínua automática e processamento LPR offline, eliminando a necessidade de processamento em tempo real.

## Fluxo de Dados

```
[Câmera RTSP]
     ↓
[MediaMTX]
  ├─ Streaming on-demand (HLS/WebRTC) → [Player Frontend]
  │   └─ Ativado apenas quando player abre
  │
  └─ Gravação contínua (sempre ativa)
        ↓
   [/recordings/cam_X/YYYY-MM-DD/HH-MM-SS.mp4]
        ↓
   [Storage Service]
     ├─ Escaneia diretório a cada 60s
     ├─ Indexa segmentos no PostgreSQL
     └─ Expõe API de consulta
        ↓
   [LPR Offline Worker]
     ├─ Busca gravações não processadas
     ├─ Processa 1 frame a cada 2s
     ├─ Detecta placas (YOLO + OCR)
     ├─ Salva eventos no banco
     └─ Marca gravação como processada
```

## Componentes

### 1. MediaMTX (Gravação)

**Configuração**: `mediamtx.yml`

```yaml
record: yes
recordPath: /recordings/%path/%Y-%m-%d/%H-%M-%S-%f
recordFormat: fmp4
recordPartDuration: 10s
recordSegmentDuration: 1h
recordDeleteAfter: 168h  # 7 dias
```

**Características**:
- Gravação contínua automática para todas as câmeras
- Segmentos de 1 hora
- Retenção de 7 dias (168h)
- Sem reencode (stream original)
- Organização: `/recordings/cam_X/YYYY-MM-DD/HH-MM-SS.mp4`

### 2. Storage Service

**Porta**: 8003  
**Tecnologia**: FastAPI + AsyncPG

**Responsabilidades**:
- Escaneia `/recordings` a cada 60 segundos
- Indexa segmentos no PostgreSQL (`recording_segments`)
- Expõe API para consulta de gravações
- Rastreia status de processamento

**Endpoints**:
- `POST /recordings/query` - Busca gravações por câmera/período
- `POST /recordings/mark-processed` - Marca como processado
- `GET /recordings/stats` - Estatísticas de armazenamento

**Tabela**: `recording_segments`
```sql
- camera_id
- file_path (único)
- start_time, end_time
- duration_seconds
- file_size_bytes
- processed (boolean)
```

### 3. LPR Offline Worker

**Tecnologia**: Python + YOLO + EasyOCR + GPU

**Funcionamento**:
1. Loop a cada 30 segundos
2. Busca câmeras ativas no banco
3. Para cada câmera, consulta gravações das últimas 2h não processadas
4. Processa vídeo:
   - 1 frame a cada 2 segundos
   - Detecção YOLO (classe 2 = veículos)
   - OCR nas regiões detectadas
   - Salva eventos com timestamp preciso
5. Marca gravação como processada

**Tabela**: `lpr_events`
```sql
- camera_id
- plate_number
- confidence
- timestamp (momento exato da detecção)
- recording_path (arquivo fonte)
- frame_offset (posição no vídeo)
- bbox_json (coordenadas)
```

### 4. Streaming Service (Atualizado)

**Mudança**: Provisiona câmeras com gravação habilitada

```python
config = {
    "source": rtsp_url,
    "sourceOnDemand": True,  # Streaming on-demand
    "record": True,          # Gravação sempre ativa
    "recordPath": f"/recordings/cam_{id}/%Y-%m-%d/%H-%M-%S-%f",
    "recordSegmentDuration": "1h",
    "recordDeleteAfter": "168h"
}
```

## Vantagens

### Performance
- **CPU/GPU**: Processamento assíncrono, não bloqueia streaming
- **Banda**: Streaming on-demand mantido (economia)
- **Escalabilidade**: Múltiplos workers LPR podem processar em paralelo

### Confiabilidade
- **Gravação**: Independente de falhas no LPR
- **Reprocessamento**: Possível reprocessar gravações antigas
- **Auditoria**: Vídeo original sempre disponível

### Operacional
- **Manutenção**: LPR pode ser atualizado sem afetar gravação
- **Debugging**: Fácil testar modelos em gravações existentes
- **Compliance**: Retenção de 7 dias para evidências

## Configuração

### Docker Compose

```yaml
storage:
  image: gtvision/storage:latest
  ports: ["8003:8003"]
  volumes:
    - mediamtx_recordings:/recordings:ro

lpr_offline:
  image: gtvision/lpr:latest
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  volumes:
    - mediamtx_recordings:/recordings:ro
```

### Variáveis de Ambiente

```env
# Storage Service
POSTGRES_HOST=postgres_db
POSTGRES_USER=gtvision_user
POSTGRES_PASSWORD=***
POSTGRES_DB=gtvision_db

# LPR Offline
STORAGE_API_URL=http://storage:8003
NVIDIA_VISIBLE_DEVICES=all
```

## Monitoramento

### Estatísticas de Armazenamento
```bash
curl http://localhost:8003/recordings/stats
```

Resposta:
```json
{
  "total_segments": 1440,
  "processed_segments": 1200,
  "pending_segments": 240,
  "total_size_gb": 125.5
}
```

### Consulta de Eventos LPR
```sql
SELECT plate_number, timestamp, confidence, camera_id
FROM lpr_events
WHERE timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY timestamp DESC;
```

## Migração

1. **Atualizar MediaMTX**: `docker-compose up -d mediamtx`
2. **Deploy Storage**: `docker-compose up -d storage`
3. **Deploy LPR Offline**: `docker-compose up -d lpr_offline`
4. **Migrar banco**: `python manage.py migrate`

## Próximos Passos

- [ ] Dashboard de monitoramento de processamento
- [ ] API de busca de placas no frontend
- [ ] Alertas em tempo real (webhook quando placa detectada)
- [ ] Exportação de clipes com detecções
- [ ] Reprocessamento seletivo de períodos
