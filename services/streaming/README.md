# GT-Vision Streaming Service

Serviço de alta performance para streaming de vídeo via HLS e WebSocket.

## 🎯 Características

- **Integração MediaMTX**: Provisiona e gerencia streams automaticamente
- **HLS Proxy**: Cache inteligente de playlists e segmentos
- **WebSocket Events**: Notificações em tempo real de status de streams
- **Alta Performance**: Async/await com FastAPI
- **Cache Redis**: Reduz carga no MediaMTX

## 🏗️ Arquitetura

```
Câmeras RTSP → MediaMTX → Streaming Service → Clientes
                  ↓
           - HLS (m3u8)
           - WebRTC
           - WebSocket Events
```

## 📡 Endpoints

### Health & Stats
```bash
GET /health              # Health check
GET /stats               # Estatísticas do serviço
```

### Câmeras
```bash
POST /cameras/provision  # Provisionar câmera no MediaMTX
DELETE /cameras/{id}     # Remover câmera
GET /cameras/{id}/info   # Info da câmera
GET /cameras/{id}/status # Status do stream
```

### Streams
```bash
GET /streams             # Listar streams
GET /streams/{path}/viewers # Contagem de viewers
```

### HLS Proxy
```bash
GET /hls/{stream}/index.m3u8  # Playlist HLS
GET /hls/{stream}/{segment}   # Segmento HLS
```

### WebSocket
```bash
WS /ws/events/{stream}   # Eventos de um stream específico
WS /ws/dashboard         # Dashboard global com stats
```

## 🚀 Quick Start

### Docker
```bash
docker build -t gtvision-streaming .
docker run -p 8001:8001 gtvision-streaming
```

### Local
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## 📊 Provisionar Câmera

```bash
curl -X POST http://localhost:8001/cameras/provision \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 1,
    "rtsp_url": "rtsp://admin:pass@192.168.1.100:554/stream",
    "name": "Camera Entrada",
    "on_demand": true
  }'
```

Resposta:
```json
{
  "success": true,
  "camera_id": 1,
  "stream_path": "cam_1",
  "hls_url": "http://mediamtx:8888/cam_1/index.m3u8",
  "webrtc_url": "http://mediamtx:8889/cam_1"
}
```

## 🔌 WebSocket Events

### Conectar a eventos de stream
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/events/cam_1');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Evento:', data.type, data);
};

// Pedir status
ws.send('status');

// Keepalive
setInterval(() => ws.send('ping'), 25000);
```

### Dashboard global
```javascript
const ws = new WebSocket('ws://localhost:8001/ws/dashboard');

ws.onmessage = (event) => {
  const { data } = JSON.parse(event.data);
  console.log('Stats:', data.active_streams, 'streams,', data.total_viewers, 'viewers');
};
```

## ⚙️ Configuração

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `MEDIAMTX_API_URL` | `http://mediamtx:9997` | URL da API do MediaMTX |
| `MEDIAMTX_HLS_URL` | `http://mediamtx:8888` | URL do servidor HLS |
| `REDIS_URL` | `redis://redis_cache:6379/2` | URL do Redis |
| `MAX_CONNECTIONS_PER_STREAM` | `100` | Limite de conexões por stream |
| `LOG_LEVEL` | `INFO` | Nível de log |

## 📈 Métricas

O serviço expõe métricas via endpoint `/stats`:

- `active_streams`: Número de streams ativos
- `total_viewers`: Total de viewers conectados
- `total_bytes_sent`: Bytes enviados
- `uptime_seconds`: Tempo de atividade

## 🔧 Performance Tuning

Para 250 câmeras:

```yaml
# docker-compose.yml
streaming:
  deploy:
    replicas: 2
    resources:
      limits:
        cpus: '2.0'
        memory: 1G
```

```bash
# Variáveis de ambiente
MAX_CONNECTIONS_PER_STREAM=200
HLS_SEGMENT_CACHE_TTL=3
```
