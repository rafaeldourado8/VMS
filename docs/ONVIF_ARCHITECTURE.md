# Arquitetura: Live vs Playback

## Fluxo Completo

```
┌─────────────────────────────────────────────────────────┐
│                    CÂMERA IP                            │
│  - Stream RTSP (live)                                   │
│  - Storage interno (SD/NVR)                             │
│  - Servidor ONVIF                                       │
└─────────────────────────────────────────────────────────┘
         │                           │
         │ RTSP live                 │ ONVIF
         ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│    MediaMTX      │        │  Serviço ONVIF   │
│  (streaming)     │        │   (playback)     │
│   :8888 HLS      │        │     :8005        │
└──────────────────┘        └──────────────────┘
         │                           │
         │ HLS live                  │ HLS playback
         ▼                           ▼
┌─────────────────────────────────────────────┐
│              FRONTEND                       │
│  - Live: usa MediaMTX                       │
│  - Playback: usa Serviço ONVIF              │
└─────────────────────────────────────────────┘
```

## 1. LIVE (não muda)

```
Câmera RTSP → MediaMTX → HLS → Frontend
```

**Exemplo:**
```
rtsp://admin:pass@192.168.1.100:554/stream
    ↓
MediaMTX converte para HLS
    ↓
http://mediamtx:8888/cam_1/index.m3u8
    ↓
Frontend toca
```

## 2. PLAYBACK (novo - ONVIF)

```
Frontend → Backend → Serviço ONVIF → Câmera Storage → HLS
```

**Passo a passo:**

### 2.1. Frontend clica na timeline (14:35)
```javascript
fetch('/onvif/playback/1/2026-02-05/14-35.m3u8')
```

### 2.2. Serviço ONVIF busca credenciais
```python
camera = await get_camera_info(1)
# {
#   "onvif_host": "192.168.1.100",
#   "onvif_port": 80,
#   "onvif_username": "admin",
#   "onvif_password": "admin123"
# }
```

### 2.3. Serviço ONVIF conecta na câmera
```python
client = ONVIFClient("192.168.1.100", 80, "admin", "admin123")
recordings = client.get_recordings(datetime(2026, 2, 5, 14, 35))
```

### 2.4. Câmera retorna token de gravação
```python
# Resposta da câmera:
{
  "token": "rec_20260205_143000",
  "earliest": "2026-02-05T14:30:00",
  "latest": "2026-02-05T15:00:00"
}
```

### 2.5. Serviço ONVIF pede URI de replay
```python
replay_uri = client.get_replay_uri("rec_20260205_143000")
# Câmera retorna:
# "rtsp://192.168.1.100:554/replay?token=rec_20260205_143000"
```

### 2.6. FFmpeg converte RTSP → HLS
```bash
ffmpeg -i "rtsp://192.168.1.100:554/replay?token=..." \
       -c copy -f hls output.m3u8
```

### 2.7. Frontend toca HLS
```javascript
videoPlayer.src = '/onvif/playback/1/2026-02-05/14-35.m3u8'
```

## Por que não usa MediaMTX?

**MediaMTX só faz streaming AO VIVO:**
- ✅ Recebe RTSP live
- ✅ Converte para HLS live
- ❌ NÃO acessa storage da câmera
- ❌ NÃO faz playback histórico
- ❌ NÃO implementa ONVIF

**Serviço ONVIF faz playback:**
- ✅ Acessa storage da câmera via ONVIF
- ✅ Busca gravações por timestamp
- ✅ Converte replay RTSP → HLS
- ✅ Independente do MediaMTX

## Configuração da Câmera

### No banco de dados:
```sql
UPDATE cameras SET
  onvif_host = '192.168.1.100',
  onvif_port = 80,
  onvif_username = 'admin',
  onvif_password = 'admin123'
WHERE id = 1;
```

### Via API:
```bash
curl -X PATCH http://localhost:8000/api/cameras/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "onvif_host": "192.168.1.100",
    "onvif_port": 80,
    "onvif_username": "admin",
    "onvif_password": "admin123"
  }'
```

## Requisitos da Câmera

Para playback ONVIF funcionar:
- ✅ Câmera com ONVIF Profile S ou G
- ✅ Recording Service habilitado
- ✅ Replay Service habilitado
- ✅ Storage configurado (SD card ou NVR)

## Testar se câmera suporta:

```python
from onvif import ONVIFCamera

cam = ONVIFCamera('192.168.1.100', 80, 'admin', 'admin123')

# Testar Recording Service
try:
    recording_service = cam.create_recording_service()
    recordings = recording_service.GetRecordings()
    print(f"✅ Gravações: {len(recordings)}")
except:
    print("❌ Recording Service não suportado")

# Testar Replay Service
try:
    replay_service = cam.create_replay_service()
    print("✅ Replay Service suportado")
except:
    print("❌ Replay Service não suportado")
```

## Vantagens

1. **Sem gravação local para playback**
   - Economiza storage
   - Usa storage da câmera

2. **Gravação local continua (para IA)**
   - Processamento offline
   - Análise de vídeo
   - Backup

3. **Escalável**
   - Cada câmera usa seu storage
   - Serviço ONVIF stateless

4. **Flexível**
   - Funciona com qualquer câmera ONVIF
   - Não depende do MediaMTX
