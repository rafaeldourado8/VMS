# Serviço ONVIF Playback

## Arquitetura

```
Câmera ONVIF (storage interno)
    ↓
Serviço ONVIF (FastAPI) :8005
    ↓ (converte RTSP replay → HLS)
Frontend (timeline)
```

## Endpoints

### 1. Listar Gravações
```
GET /cameras/{camera_id}/recordings/{date}
    ?camera_ip=192.168.1.100
    &username=admin
    &password=admin123
    &port=80

Response:
[
  {
    "start": "2026-02-05T08:00:00",
    "end": "2026-02-05T18:00:00",
    "type": "onvif",
    "token": "recording_token_123"
  }
]
```

### 2. Playback HLS
```
GET /playback/{camera_id}/{date}/{time}.m3u8
    ?camera_ip=192.168.1.100
    &username=admin
    &password=admin123
    &port=80

Response: HLS manifest
```

### 3. Segmentos HLS
```
GET /playback/{camera_id}/{date}/{time}_{segment}.ts
```

## Como Funciona

1. **Frontend clica na timeline**
2. **Busca gravações ONVIF** da câmera
3. **Serviço ONVIF** pede replay URI para a câmera
4. **Câmera retorna** RTSP do storage interno
5. **FFmpeg converte** RTSP → HLS on-demand
6. **Player toca** o HLS gerado

## Vantagens

- ✅ Sem gravação local para playback
- ✅ Usa storage da câmera
- ✅ Funciona com qualquer câmera ONVIF
- ✅ Gravação local continua (para IA)

## Integração Frontend

```typescript
// Buscar gravações ONVIF
const response = await fetch(
  `/onvif/cameras/${cameraId}/recordings/${date}?` +
  `camera_ip=${camera.ip}&username=${camera.user}&password=${camera.pass}`
)
const recordings = await response.json()

// Playback
const playbackUrl = 
  `/onvif/playback/${cameraId}/${date}/${time}.m3u8?` +
  `camera_ip=${camera.ip}&username=${camera.user}&password=${camera.pass}`

setVideoSrc(playbackUrl)
```

## Configuração

### Docker Compose
```yaml
onvif:
  build: ./services/onvif
  ports:
    - "8005:8005"
```

### Iniciar
```bash
docker-compose up -d onvif
```

### Logs
```bash
docker logs -f gtvision_onvif
```

## Requisitos da Câmera

A câmera precisa suportar:
- ✅ ONVIF Profile S ou G
- ✅ Recording Service
- ✅ Replay Service
- ✅ Storage interno (SD card ou NVR)

## Testar ONVIF

```python
from onvif import ONVIFCamera

cam = ONVIFCamera('192.168.1.100', 80, 'admin', 'admin123')

# Testar serviços
recording_service = cam.create_recording_service()
recordings = recording_service.GetRecordings()

print(f"Gravações encontradas: {len(recordings)}")
```

## Troubleshooting

### Erro: "No recordings found"
- Verificar se câmera tem storage configurado
- Verificar se há gravações no período
- Testar com ONVIF Device Manager

### Erro: "Failed to get replay URI"
- Câmera pode não suportar Replay Service
- Verificar credenciais ONVIF
- Testar porta (geralmente 80 ou 8080)

### Erro: "FFmpeg failed"
- Verificar se RTSP replay está acessível
- Testar URL com VLC: `rtsp://...`
- Verificar firewall

## Próximos Passos

1. Adicionar cache de manifests (5min)
2. Suportar múltiplos tokens de gravação
3. Implementar busca por eventos
4. Adicionar suporte a PTZ durante playback
