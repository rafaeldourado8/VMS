# 🐳 Deploy Docker - AI Detection + Frontend

## 🚀 Quick Start

```bash
# 1. Build e iniciar tudo
docker-compose up -d --build

# 2. Verificar serviços
docker-compose ps

# 3. Ver logs
docker-compose logs -f ai_detection_new backend frontend
```

## ✅ Verificar Funcionamento

### 1. Backend + WebSocket
```bash
# Health check
curl http://localhost:8000/api/health

# WebSocket (deve conectar)
# Abrir browser console em http://localhost:5173
# Deve ver: "WebSocket connected"
```

### 2. AI Detection
```bash
# Health check
curl http://localhost:5001/health

# Listar câmeras ativas
curl http://localhost:5001/cameras

# Iniciar câmera (se já existe no MediaMTX)
curl -X POST http://localhost:5001/camera/start \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 1}'
```

### 3. Frontend
```
http://localhost:5173/detections
```

## 📊 Fluxo Completo

```
1. Camera RTSP → MediaMTX (porta 8889 WebRTC)
2. AI Detection (porta 5001) → Processa frames
3. RabbitMQ → Recebe detecções
4. Backend Consumer → Consome RabbitMQ
5. WebSocket (ws://backend:8000/ws/detections) → Broadcast
6. Frontend (porta 5173) → Exibe em tempo real
```

## 🔧 Serviços e Portas

| Serviço | Porta | URL |
|---------|-------|-----|
| Frontend | 5173 | http://localhost:5173 |
| Backend | 8000 | http://localhost:8000 |
| AI Detection | 5001 | http://localhost:5001 |
| MediaMTX API | 9997 | http://localhost:9997 |
| MediaMTX WebRTC | 8889 | http://localhost:8889 |
| MediaMTX HLS | 8888 | http://localhost:8888 |
| RabbitMQ Mgmt | 15672 | http://localhost:15672 |
| Prometheus | 9090 | http://localhost:9090 |

## 🧪 Testar Detecção

### Opção 1: Câmera Real
```bash
# 1. Adicionar câmera no MediaMTX (via Streaming Service)
# Frontend → Câmeras → Adicionar Câmera

# 2. Iniciar processamento IA
curl -X POST http://localhost:5001/camera/start \
  -d '{"camera_id": 1}'

# 3. Ver detecções
# http://localhost:5173/detections
```

### Opção 2: Teste Manual (Simular Detecção)
```bash
# Enviar detecção fake para RabbitMQ
docker exec -it gtvision_rabbitmq rabbitmqadmin publish \
  exchange=vms.detections \
  routing_key=detection.lpr.1 \
  payload='{"id":"test-123","camera_id":1,"plate":"TEST123","confidence":0.95,"method":"simple_majority","timestamp":"2024-01-15T10:00:00Z","metadata":{"track_id":1,"frames_analyzed":10,"votes":5,"total":5}}'

# Deve aparecer no frontend instantaneamente
```

## 📝 Logs Importantes

```bash
# Backend (consumer + websocket)
docker logs -f gtvision_backend | grep -E "WebSocket|Detection|consumer"

# AI Detection (processamento)
docker logs -f gtvision_ai_detection_new | grep -E "Detection sent|WebRTC|camera"

# RabbitMQ (mensagens)
docker logs -f gtvision_rabbitmq | grep -E "published|delivered"
```

## ⚠️ Troubleshooting

### Frontend não conecta WebSocket
```bash
# 1. Verificar backend rodando
docker logs gtvision_backend | grep "Daphne"

# 2. Verificar consumer iniciado
docker logs gtvision_backend | grep "consumer started"

# 3. Testar WebSocket manualmente
# Browser console:
const ws = new WebSocket('ws://localhost:8000/ws/detections')
ws.onopen = () => console.log('Connected!')
```

### AI Detection não envia
```bash
# 1. Verificar logs
docker logs gtvision_ai_detection_new

# 2. Verificar RabbitMQ
curl -u guest:guest http://localhost:15672/api/exchanges/%2F/vms.detections

# 3. Verificar câmera processando
curl http://localhost:5001/cameras
```

### Detecções não aparecem
```bash
# 1. Verificar WebSocket conectado (indicador verde)
# 2. Verificar console do browser (F12)
# 3. Enviar detecção teste (ver Opção 2 acima)
```

## 🔄 Restart Serviços

```bash
# Restart tudo
docker-compose restart

# Restart específico
docker-compose restart backend
docker-compose restart ai_detection_new
docker-compose restart frontend

# Rebuild se mudou código
docker-compose up -d --build backend
docker-compose up -d --build ai_detection_new
```

## 📊 Monitoramento

### RabbitMQ Management
```
http://localhost:15672
user: guest
pass: guest

Ir em: Exchanges → vms.detections → Ver mensagens
```

### Prometheus
```
http://localhost:9090

Queries úteis:
- rate(detections_total[5m])
- ai_detection_fps
- websocket_connections
```

## ✅ Checklist de Sucesso

- [ ] Backend rodando (porta 8000)
- [ ] Consumer iniciado (logs: "consumer started")
- [ ] AI Detection rodando (porta 5001)
- [ ] Frontend rodando (porta 5173)
- [ ] WebSocket conectado (indicador verde)
- [ ] Câmera processando (logs AI Detection)
- [ ] Detecções aparecem no frontend (<1s)
- [ ] RabbitMQ recebendo mensagens
- [ ] Sem duplicatas (mesmo veículo não aparece 2x)

## 🎯 Pronto!

Tudo configurado para rodar em Docker. Acesse:
```
http://localhost:5173/detections
```

E veja as detecções em tempo real! 🚀
