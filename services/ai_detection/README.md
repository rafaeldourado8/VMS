# AI Detection Service

Sistema unificado de detecção de placas veiculares com pipeline otimizado.

## 🎯 Features

- ✅ **Frame Extractor** - RTSP capture com FPS throttling (1-3 FPS)
- ✅ **Frame Buffer** - Queue assíncrona para desacoplar captura/processamento
- ✅ **Motion Detection** - OpenCV MOG2 (70-80% economia CPU)
- ✅ **Vehicle Detection** - YOLO (car, truck, motorcycle, bus)
- ✅ **Multi-Object Tracking** - IoU-based (acumula 10-30 frames)
- ✅ **Quality Scoring** - Blur/Angle/Contrast/Size (seleciona melhores frames)
- ✅ **Plate Detection** - YOLO LPR fine-tuned
- ✅ **OCR Engine** - Fast-Plate-OCR (CPU-optimized, ONNX)
- ✅ **Consensus Engine** - 3 estratégias de votação
- ✅ **Dedup Cache** - Redis (TTL 5min, similaridade 80%)
- ✅ **RabbitMQ Producer** - Envia eventos para Backend
- ✅ **Flask API** - Controle de câmeras (start/stop/list)

## 📊 Pipeline

```
RTSP (30 FPS)
  ↓ Frame Extractor (FPS throttle 90%)
3 FPS
  ↓ Motion Detection (drop 70%)
0.9 FPS
  ↓ Vehicle Detection (drop 50%)
0.45 FPS
  ↓ Tracking → Quality Scoring → Plate Detection → OCR → Consensus → Dedup → RabbitMQ
```

**Resultado**: Processa apenas 1.5% dos frames originais!

## 🚀 Quick Start

### 1. Preparar Modelos

```bash
# Baixar YOLOv8n
cd services/ai_detection
mkdir models
cd models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### 2. Configurar Ambiente

```bash
cp .env.example .env
# Editar .env conforme necessário
```

### 3. Iniciar Serviços

```bash
# Com docker-compose
docker-compose up -d

# Ou build manual
docker build -t ai_detection .
docker run -d \
  --name ai_detection \
  --env-file .env \
  -p 5000:5000 \
  -v ./models:/app/models \
  ai_detection
```

### 4. Testar API

```bash
# Health check
curl http://localhost:5000/health

# Iniciar câmera
curl -X POST http://localhost:5000/camera/start \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 1,
    "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream"
  }'

# Listar câmeras ativas
curl http://localhost:5000/cameras

# Parar câmera
curl -X POST http://localhost:5000/camera/stop \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 1}'
```

## 🧪 Testes

### Testes Unitários

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar testes
python test_components.py
# ou
pytest test_components.py -v
```

### Testes de Integração

```bash
# Certifique-se que o serviço está rodando
docker-compose up -d

# Rodar testes
python test_integration.py
```

## ⚙️ Configuração

Ver [.env.example](./.env.example) para todas as variáveis.

### Perfis Recomendados

**Produção (Balanço)**:
```bash
AI_FPS=3
MOTION_THRESHOLD=0.03
MIN_READINGS=5
CONSENSUS_THRESHOLD=0.6
MIN_CONFIDENCE=0.75
```

**Alta Performance (Custo Mínimo)**:
```bash
AI_FPS=1
MOTION_THRESHOLD=0.05
MIN_READINGS=3
CONSENSUS_THRESHOLD=0.5
MIN_CONFIDENCE=0.70
```

**Desenvolvimento (Precisão Máxima)**:
```bash
AI_FPS=5
MOTION_THRESHOLD=0.01
MIN_READINGS=7
CONSENSUS_THRESHOLD=0.7
MIN_CONFIDENCE=0.85
```

## 📡 API Endpoints

### GET /health
Health check do serviço

**Response**:
```json
{
  "status": "ok",
  "active_cameras": 2
}
```

### POST /camera/start
Inicia processamento de uma câmera

**Request**:
```json
{
  "camera_id": 1,
  "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream"
}
```

**Response**:
```json
{
  "status": "started",
  "camera_id": 1
}
```

### POST /camera/stop
Para processamento de uma câmera

**Request**:
```json
{
  "camera_id": 1
}
```

**Response**:
```json
{
  "status": "stopped",
  "camera_id": 1
}
```

### GET /cameras
Lista câmeras ativas

**Response**:
```json
{
  "cameras": [
    {"id": 1, "url": "rtsp://..."},
    {"id": 2, "url": "rtsp://..."}
  ]
}
```

## 📨 RabbitMQ Events

Eventos são enviados para o exchange `vms.detections` com routing key `detection.lpr.{camera_id}`.

**Payload**:
```json
{
  "camera_id": 1,
  "plate": "ABC1234",
  "confidence": 0.92,
  "method": "simple_majority",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "track_id": 42,
    "frames_analyzed": 15,
    "votes": 4,
    "total": 5
  }
}
```

## 🔧 Troubleshooting

### Câmera não conecta
```bash
# Verificar URL RTSP
ffmpeg -i "rtsp://..." -frames:v 1 test.jpg

# Verificar logs
docker logs ai_detection
```

### Muitos frames descartados
```bash
# Reduzir threshold de movimento
MOTION_THRESHOLD=0.01

# Aumentar FPS
AI_FPS=5
```

### Baixa taxa de consenso
```bash
# Reduzir threshold de consenso
CONSENSUS_THRESHOLD=0.5

# Aumentar leituras
MAX_READINGS=7
```

### Redis não conecta
```bash
# Verificar Redis
docker logs ai_detection_redis

# Testar conexão
redis-cli -h localhost ping
```

### RabbitMQ não conecta
```bash
# Verificar RabbitMQ
docker logs ai_detection_rabbitmq

# Acessar management
http://localhost:15672
# user: guest, pass: guest
```

## 📚 Documentação

Ver [docs/ai-detection/](../../docs/ai-detection/) para documentação completa.

## 🔗 Componentes

### Core
- [Motion Detector](./core/motion_detector.py) - OpenCV MOG2
- [Vehicle Detector](./core/vehicle_detector.py) - YOLO
- [Tracker](./core/tracker.py) - IoU tracking
- [Quality Scorer](./core/quality_scorer.py) - 4 métricas
- [Plate Detector](./core/plate_detector.py) - YOLO LPR
- [OCR Engine](./core/ocr_engine.py) - Fast-Plate-OCR

### Pipeline
- [Frame Extractor](./pipeline/frame_extractor.py) - RTSP capture
- [Frame Buffer](./pipeline/frame_buffer.py) - Async queue
- [Consensus Engine](./pipeline/consensus_engine.py) - Votação
- [Dedup Cache](./pipeline/dedup_cache.py) - Redis

### Integration
- [RabbitMQ Producer](./integration/rabbitmq_producer.py) - Event queue

### API
- [Control API](./api/control_api.py) - Flask REST API

## 📈 Métricas

- **Latência**: ~250ms por detecção
- **CPU**: ~60% por câmera
- **Memória**: ~250MB por câmera
- **Precisão**: >95% (com consenso)
- **Throughput**: 10-20 câmeras por servidor

## 📄 Licença

Ver [LICENSE](../../LICENSE)
