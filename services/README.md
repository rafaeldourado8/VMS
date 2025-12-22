# GT-Vision Services

Esta pasta contém os microsserviços especializados do GT-Vision VMS.

## 📁 Estrutura

```
services/
├── streaming/          # Serviço de streaming HLS/WebSocket
│   ├── main.py         # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
│
└── ai-service/         # Serviço de IA (YOLO, LPR)
    ├── main.py         # FastAPI app
    ├── detector.py     # YOLO detector
    ├── docker-compose.yml  # ⚠️ Separado (build pesado)
    └── Dockerfile
```

## 🎬 Streaming Service

Serviço de alta performance para streaming de vídeo.

**Funcionalidades:**
- Proxy HLS com cache Redis
- WebSocket para eventos em tempo real
- Provisionamento automático de câmeras no MediaMTX
- Estatísticas de viewers

**Build rápido:** ~30 segundos

```bash
# Já incluído no docker-compose.yml principal
docker-compose up -d streaming
```

## 🤖 AI Service

Serviço de detecção de veículos e placas usando YOLO.

**Funcionalidades:**
- Detecção de veículos (car, truck, bus, motorcycle)
- Reconhecimento de placas (LPR) - opcional
- Fila assíncrona com Redis
- Métricas Prometheus

**⚠️ Build pesado:** ~10-15 minutos (PyTorch, YOLO, OpenCV)

```bash
# Build separado (uma vez)
cd services/ai-service
docker-compose build

# Iniciar
docker-compose up -d
```

## 🚀 Ordem de Inicialização

```bash
# 1. Infraestrutura + Serviços principais
docker-compose up -d

# 2. AI Service (opcional, separado)
cd services/ai-service
docker-compose up -d
```

## 📊 Portas

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Streaming | 8001 | API REST + WebSocket |
| AI Service | 8080 | API REST |
| AI Service | 9092 | Métricas Prometheus |

## 🔗 Comunicação

```
HAProxy (80)
    ├─→ /streaming/* → Streaming Service (8001)
    ├─→ /ai/*        → AI Service (8080)
    ├─→ /hls/*       → MediaMTX (8888) [bypass]
    └─→ /api/*       → Kong → Django
```

## 🛠️ Desenvolvimento

### Streaming Service
```bash
cd services/streaming
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### AI Service
```bash
cd services/ai-service
pip install -r requirements.txt
python main.py
```

## 📝 Variáveis de Ambiente

### Streaming
```env
MEDIAMTX_API_URL=http://mediamtx:9997
REDIS_URL=redis://redis_cache:6379/2
```

### AI Service
```env
REDIS_HOST=redis_cache
WORKERS=4
ENABLE_GPU=false
```
