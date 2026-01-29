# Sistema de Detecção Automática LPR

## Fluxo Automático

```
1. Adicionar Câmera RTSP
   └─> Backend Django → POST /api/cameras/provision
       └─> Streaming Service recebe requisição
           └─> Provisiona stream no MediaMTX (cam_123)
           └─> Publica mensagem no Redis: "camera:provisioned"

2. LPR Manager (escutando Redis)
   └─> Recebe notificação da nova câmera
       └─> Inicia LPRStreamService automaticamente
           ├─> Input:  rtsp://mediamtx:8554/cam_123 (stream original)
           ├─> Processa: Detecção de placas com YOLO + PaddleOCR
           └─> Output: rtsp://mediamtx:8554/cam_123_ai (stream com anotações)

3. Visualização
   ├─> Stream Original: /hls/cam_123/index.m3u8
   └─> Stream com IA:   /hls/cam_123_ai/index.m3u8
```

## Endpoints

### Streaming Service (porta 8001)
- `POST /cameras/provision` - Adiciona câmera e dispara LPR
- `GET /cameras/{id}/status` - Status da câmera
- `GET /hls/{path}/{file}` - Proxy HLS

### LPR Service (porta 8080)
- `GET /health` - Status do serviço
- `GET /streams` - Lista streams LPR ativos

## Snapshots

Salvos automaticamente em `/app/snapshots/cam_{id}/{timestamp}_{uuid}/`:
- `vehicle.jpg` - Crop do veículo
- `full_frame.jpg` - Frame completo
- `metadata.json` - Dados da detecção

## Exemplo de Uso

```bash
# Adicionar câmera RTSP
curl -X POST http://localhost:8001/cameras/provision \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 1,
    "rtsp_url": "rtsp://usuario:senha@192.168.1.100:554/stream",
    "name": "Câmera Entrada",
    "enabled": true,
    "on_demand": false
  }'

# Verificar streams LPR ativos
curl http://localhost:8080/streams

# Assistir stream com detecção
# http://localhost:8888/cam_1_ai/index.m3u8
```

## Variáveis de Ambiente

```env
REDIS_URL=redis://redis_cache:6379/2
MEDIAMTX_API_URL=http://mediamtx:9997
```
