# 🧪 Guia de Teste - AI Detection + Frontend

## 🎯 Objetivo
Testar o fluxo completo: AI Detection → RabbitMQ → Backend → WebSocket → Frontend

## 📋 Pré-requisitos

1. **Serviços rodando**:
   - MediaMTX (porta 8889 WebRTC, 9997 API)
   - Redis (porta 6379)
   - RabbitMQ (porta 5672, 15672 management)
   - Backend Django (porta 8000)
   - Frontend React (porta 5173)
   - AI Detection (porta 5000)

## 🚀 Passo a Passo

### 1. Iniciar Todos os Serviços

```bash
# Root do projeto
cd d:\VMS

# Iniciar infraestrutura
docker-compose up -d postgres_db redis rabbitmq mediamtx

# Iniciar backend
cd backend
python manage.py runserver

# Em outro terminal - Iniciar consumer
cd backend
python start_consumer.py

# Em outro terminal - Iniciar frontend
cd frontend
npm run dev

# Em outro terminal - Iniciar AI Detection
cd services/ai_detection
docker-compose up -d
```

### 2. Verificar Serviços

```bash
# MediaMTX
curl http://localhost:9997/v3/config/global/get

# RabbitMQ
curl -u guest:guest http://localhost:15672/api/overview

# AI Detection
curl http://localhost:5000/health

# Backend
curl http://localhost:8000/api/health
```

### 3. Adicionar Câmera no MediaMTX

```bash
# Via API do MediaMTX (se ainda não tiver)
curl -X POST http://localhost:9997/v3/config/paths/add/camera_1 \
  -H "Content-Type: application/json" \
  -d '{
    "source": "rtsp://admin:password@192.168.1.100:554/stream",
    "sourceOnDemand": false
  }'
```

### 4. Iniciar Processamento IA

```bash
# Iniciar AI Detection para camera_1
curl -X POST http://localhost:5000/camera/start \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 1}'

# Verificar logs
docker logs -f ai_detection
```

### 5. Abrir Frontend

```
http://localhost:5173/detections
```

## ✅ O que Você Deve Ver

### No Frontend (http://localhost:5173/detections)

1. **Indicador de Conexão**: 
   - 🟢 Verde "Conectado" (WebSocket ativo)

2. **Quando uma placa for detectada**:
   ```
   ┌─────────────────────────────────────┐
   │ ABC1234  [Maioria]                  │
   │ 📷 Câmera 1  ✓ 4/5 votos  15 frames│
   │                          92%  há 2s │
   └─────────────────────────────────────┘
   ```

### Nos Logs do AI Detection

```bash
docker logs -f ai_detection

# Você verá:
# INFO - WebRTC enabled: True
# INFO - Using WebRTC for camera 1: http://mediamtx:8889/camera_1/whep
# INFO - Processing camera 1
# INFO - Detection sent: ABC1234 (conf: 0.92, method: simple_majority)
```

### Nos Logs do Backend Consumer

```bash
# Terminal onde rodou start_consumer.py

# Você verá:
# Detection consumer started
# WebSocket connected. Total: 1
# Broadcasting detection: ABC1234
```

### No RabbitMQ Management (http://localhost:15672)

1. Login: `guest` / `guest`
2. Ir em **Exchanges** → `vms.detections`
3. Ver mensagens sendo publicadas
4. Ir em **Queues** → `detections_websocket`
5. Ver mensagens sendo consumidas

## 🔍 Troubleshooting

### Frontend não conecta WebSocket

```bash
# Verificar backend rodando
curl http://localhost:8000/api/health

# Verificar consumer rodando
ps aux | grep start_consumer

# Ver logs do browser
# F12 → Console → Procurar por "WebSocket"
```

### AI Detection não envia detecções

```bash
# Verificar RabbitMQ
docker logs rabbitmq

# Verificar AI Detection
docker logs ai_detection | grep "Detection sent"

# Verificar se câmera está processando
curl http://localhost:5000/cameras
```

### Detecções não aparecem no Frontend

```bash
# 1. Verificar WebSocket conectado (indicador verde)
# 2. Verificar console do browser (F12)
# 3. Verificar consumer backend rodando
# 4. Testar envio manual:

# No Python (terminal backend):
python
>>> from infrastructure.websocket.detection_manager import manager
>>> import asyncio
>>> asyncio.run(manager.broadcast({
...     'id': 'test-123',
...     'camera_id': 1,
...     'plate': 'TEST123',
...     'confidence': 0.95,
...     'method': 'simple_majority',
...     'timestamp': '2024-01-15T10:00:00Z',
...     'metadata': {
...         'track_id': 1,
...         'frames_analyzed': 10,
...         'votes': 5,
...         'total': 5
...     }
... }))
```

## 📊 Fluxo Completo

```
1. Câmera RTSP
   ↓
2. MediaMTX (WebRTC)
   ↓
3. AI Detection
   - Motion Detection (drop 70%)
   - Vehicle Detection
   - Tracking (10-30 frames)
   - Quality Scoring
   - Plate Detection
   - OCR (3-5 leituras)
   - Consensus (≥60%)
   - Dedup (Redis 5min)
   ↓
4. RabbitMQ (exchange: vms.detections)
   ↓
5. Backend Consumer
   ↓
6. WebSocket Manager
   ↓
7. Frontend (Tempo Real)
```

## 🎯 Teste de Sucesso

✅ **Tudo funcionando se**:
1. Frontend mostra "Conectado" (verde)
2. AI Detection processa frames (logs)
3. Detecções aparecem no frontend em <1s
4. Placa, confiança e método corretos
5. Sem duplicatas (mesmo veículo não aparece 2x em 5min)

## 📝 Notas

- **Latência esperada**: <1 segundo (detecção → frontend)
- **FPS processado**: 1-3 FPS (economia 90%)
- **Precisão**: >95% (com consenso)
- **HLS não afetado**: Usuários continuam vendo stream normal
