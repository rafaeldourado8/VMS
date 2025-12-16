# 🚀 ROADMAP TÉCNICO - GT-Vision Split-Brain Architecture

**Meta:** MVP para 250 câmeras até final de Janeiro 2025  
**Arquitetura:** Split-Brain com GPU Workers dedicados para IA

---

## 📐 VISÃO GERAL DA ARQUITETURA

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EDGE / CDN                                      │
│  ┌──────────────┐    ┌──────────────┐                                       │
│  │  CloudFlare  │    │   WAF/DDoS   │                                       │
│  │    (CDN)     │    │  Protection  │                                       │
│  └──────┬───────┘    └──────┬───────┘                                       │
│         └──────────┬────────┘                                               │
│                    ▼                                                         │
│         ┌──────────────────┐                                                │
│         │  HAProxy Nodes   │ ← Stats Dashboard :8404                        │
│         │  (Load Balancer) │                                                │
│         └────────┬─────────┘                                                │
└──────────────────┼──────────────────────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
┌───────────────┐     ┌───────────────┐
│  /video_api   │     │ static_files  │
│     Kong      │     │    Nginx      │
│ (API Gateway) │     │   (:8080)     │
└───────┬───────┘     └───────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY (Kong/KongDB)                            │
│  Rate Limiting │ JWT Auth │ Routing │ SSL Termination                       │
│  ┌────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐                            │
│  │ Kong DB│ │Cassandra│ │Auth/JWT │ │ Logging  │                            │
│  └────────┘ └─────────┘ └─────────┘ └──────────┘                            │
└─────────────────────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAMADA SET 01 (API Workers)                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ Backend Django  │  │ Auth/Identity   │  │ Gateway FastAPI │              │
│  │  • REST API     │  │   Keycloak      │  │  • Bulk Ingest  │              │
│  │  • Admin        │  │  • SSO          │  │  • WebSocket    │              │
│  │  • ORM          │  │  • LDAP         │  │  • Async        │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAMADA SET 02 (AI Workers)                            │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              Frame Grabber Service (FastAPI + AI)                    │    │
│  │         Alta Disponibilidade - Suporte GPU Local + AWS               │    │
│  │                                                                       │    │
│  │  ┌─────────────────────────────┐  ┌─────────────────────────────┐   │    │
│  │  │     GPU WORKERS (Local)     │  │    AWS WORKERS (EC2)        │   │    │
│  │  │  ┌───────┐ ┌───────┐       │  │  ┌───────┐ ┌───────┐        │   │    │
│  │  │  │GPU #1 │ │GPU #2 │       │  │  │EC2 #1 │ │EC2 #N │        │   │    │
│  │  │  │YOLO   │ │YOLO   │       │  │  │Rekog. │ │Rekog. │        │   │    │
│  │  │  │TF/LPR │ │TF/LPR │       │  │  │API    │ │API    │        │   │    │
│  │  │  │CUDA   │ │CUDA   │       │  │  │       │ │       │        │   │    │
│  │  │  └───────┘ └───────┘       │  │  └───────┘ └───────┘        │   │    │
│  │  │     ~50ms latency          │  │     ~200ms latency          │   │    │
│  │  │     Custo fixo             │  │     Pay-per-use             │   │    │
│  │  └─────────────────────────────┘  └─────────────────────────────┘   │    │
│  │                         ↓                                            │    │
│  │         ┌───────────────────────────────────┐                       │    │
│  │         │     HYBRID PROVIDER               │                       │    │
│  │         │  • Primary: GPU (baixa latência)  │                       │    │
│  │         │  • Fallback: AWS (alta escala)    │                       │    │
│  │         │  • Circuit Breaker automático     │                       │    │
│  │         └───────────────────────────────────┘                       │    │
│  │                         ↓                                            │    │
│  │              Batch Processing (Frames + Detections)                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAMADA DE MENSAGERIA                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ PostgreSQL      │  │ Redis Cluster   │  │ MinIO (S3)      │              │
│  │  • Primary      │  │  • Cache API    │  │ Object Storage  │              │
│  │  • Replica RO   │  │  • Pub/Sub      │  │  • Frames       │              │
│  │  • PgBouncer    │  │  • Sessions     │  │  • Recordings   │              │
│  │  • Backup       │  │  • Rate Limit   │  │  • Replicação   │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       OBSERVABILIDADE                                        │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐                 │
│  │Prometheus │  │ Grafana   │  │   Loki    │  │  Jaeger   │                 │
│  │ (Metrics) │  │(Dashboard)│  │  (Logs)   │  │ (Tracing) │                 │
│  └─────┬─────┘  └───────────┘  └───────────┘  └───────────┘                 │
│        │                                                                     │
│        ▼                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │              Alertmanager → PagerDuty / Slack                        │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    AWS CloudWatch (EC2 Workers)                      │    │
│  │              • Billing Alerts • Auto Scaling Metrics                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 FASE 1: INFRAESTRUTURA CORE (Semana 1-2)

### ~~1.1 Implementar HAProxy como Load Balancer Principal~~ ✅
**Objetivo:** Segregar tráfego de vídeo do tráfego de API na entrada.

**Tarefas:**
- [x] Criar `haproxy/haproxy.cfg` com ACLs para detectar rotas de vídeo
- [x] Configurar backend para MediaMTX (porta 8888 HLS, 8889 WebRTC, 8554 RTSP)
- [x] Configurar backend para API (Kong/WAF → Gateway → Django)
- [x] Configurar backend para Frontend (Nginx estático)
- [x] Adicionar health checks para todos backends
- [x] Configurar sticky sessions para WebRTC
- [x] Adicionar ao `docker-compose.yml` como serviço principal (porta 80/443)

**Implementado:** `haproxy/haproxy.cfg` + `docker-compose.yml`
- Split-brain: Vídeo → MediaMTX direto (bypass API)
- API → Gateway → Django
- Estáticos → Nginx (porta 8080)
- Sticky sessions para WebRTC
- Health checks: 10s interval
- Stats dashboard: http://localhost:8404/stats

**Validação:**
- [x] HAProxy rodando na porta 80
- [x] ACLs segregando tráfego corretamente
- [x] Health checks funcionando

---

### ~~1.2 Otimizar MediaMTX para 250 Câmeras~~ ✅
**Objetivo:** Garantir que MediaMTX suporte carga sem gargalos.

**Tarefas:**
- [x] Ajustar `mediamtx.yml` para alta concorrência
- [x] Configurar gravação em disco com rotação automática (7 dias)
- [x] Habilitar API de métricas (porta 9998)
- [x] Configurar paths dinâmicos para câmeras (`cam_{id}`)
- [x] Testar reconexão automática de streams RTSP
- [x] Configurar HLS com segmentos otimizados

**Implementado:** `mediamtx.yml` otimizado
- writeQueueSize: 1024 (buffer para 250 câmeras)
- HLS: 2s segments, 3 count (equilíbrio latência/carga)
- Gravação: fmp4, 1h segments, 7d retenção
- API: porta 9997, Metrics: porta 9998
- maxReaders: 100 por stream
- sourceOnDemand: yes (economiza recursos)

**Validação:**
- [x] 6 câmeras reais configuradas e testadas
- [x] API funcionando (porta 9997)
- [x] Metrics habilitadas (porta 9998)
- [x] Gravações em `/recordings` com rotação 7d

---

### ~~1.3 Configurar Nginx como Servidor Estático~~ ✅
**Objetivo:** Nginx serve apenas frontend e arquivos estáticos (não faz proxy de vídeo).

**Tarefas:**
- [x] Simplificar `nginx/nginx.conf` removendo proxies de vídeo
- [x] Manter apenas: frontend, /static/, /media/
- [x] Configurar cache agressivo para assets (7 dias)
- [x] Adicionar compressão gzip/brotli
- [x] Configurar HTTP/2

**Implementado:** `nginx/nginx.simple.conf` (30 linhas vs 300)
- Apenas serve `/static/` e `/media/` na porta 8080
- Removidos todos os proxies (HAProxy faz roteamento direto)
- Economia: 90% memória (~5MB vs ~50MB)

**Validação:**
- [x] Config validada com `nginx -t`
- [x] Assets estáticos servidos com cache headers
- [x] Vídeo NÃO passa por Nginx (HAProxy → MediaMTX direto)

---

### ~~1.4 Implementar Kong API Gateway~~ ✅
**Objetivo:** Substituir roteamento direto por API Gateway enterprise-grade.

**Tarefas:**
- [x] Adicionar Kong (DB-less mode) ao `docker-compose.yml`
- [x] Configurar rate limiting global e por rota
- [x] Configurar CORS
- [x] Configurar Prometheus metrics
- [x] Criar rotas para Django, Gateway FastAPI
- [x] Configurar health checks
- [x] Integrar com HAProxy
- [ ] Configurar JWT validation plugin (após Keycloak)

**docker-compose.yml:**
```yaml
kong-database:
  image: postgres:15-alpine
  environment:
    POSTGRES_USER: kong
    POSTGRES_DB: kong
    POSTGRES_PASSWORD: ${KONG_DB_PASSWORD}
  volumes:
    - kong_data:/var/lib/postgresql/data
  healthcheck:
    test: ["CMD", "pg_isready", "-U", "kong"]
    interval: 10s
    timeout: 5s
    retries: 5

kong-migrations:
  image: kong:3.5
  command: kong migrations bootstrap
  environment:
    KONG_DATABASE: postgres
    KONG_PG_HOST: kong-database
    KONG_PG_USER: kong
    KONG_PG_PASSWORD: ${KONG_DB_PASSWORD}
  depends_on:
    kong-database:
      condition: service_healthy

kong:
  image: kong:3.5
  environment:
    KONG_DATABASE: postgres
    KONG_PG_HOST: kong-database
    KONG_PG_USER: kong
    KONG_PG_PASSWORD: ${KONG_DB_PASSWORD}
    KONG_PROXY_ACCESS_LOG: /dev/stdout
    KONG_ADMIN_ACCESS_LOG: /dev/stdout
    KONG_PROXY_ERROR_LOG: /dev/stderr
    KONG_ADMIN_ERROR_LOG: /dev/stderr
    KONG_ADMIN_LISTEN: 0.0.0.0:8001
    KONG_ADMIN_GUI_LISTEN: 0.0.0.0:8002
  ports:
    - "8000:8000"   # Proxy
    - "8001:8001"   # Admin API
    - "8002:8002"   # Kong Manager GUI
  depends_on:
    kong-migrations:
      condition: service_completed_successfully
  healthcheck:
    test: ["CMD", "kong", "health"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Configuração de rotas (via Admin API):**
```bash
# Criar serviço Django
curl -X POST http://localhost:8001/services \
  --data name=django-api \
  --data url=http://django:8000

# Criar rota
curl -X POST http://localhost:8001/services/django-api/routes \
  --data paths[]=/api \
  --data strip_path=false

# Habilitar rate limiting
curl -X POST http://localhost:8001/services/django-api/plugins \
  --data name=rate-limiting \
  --data config.minute=100 \
  --data config.policy=local

# Habilitar JWT
curl -X POST http://localhost:8001/services/django-api/plugins \
  --data name=jwt
```

**Implementado:** `kong/kong.yml` + `docker-compose.yml` + `haproxy/haproxy.cfg`
- DB-less mode (sem PostgreSQL/Cassandra extra)
- Rate limiting: /api (100/min), /fast-api (1000/min), /admin (30/min)
- CORS configurado para frontend
- Prometheus metrics em /metrics
- Request/Correlation IDs para tracing
- HAProxy → Kong → Django/Gateway

**Validação:**
- [x] Kong rodando e acessível (:8000)
- [x] Kong Manager GUI funcionando (:8002)
- [x] Admin API funcionando (:8001)
- [x] Rate limiting configurado
- [x] CORS funcionando
- [x] HAProxy roteando para Kong
- [x] Health checks passando
- [x] Rota de static files funcionando (16/12/2024)
- [x] Django Admin acessível via Kong (16/12/2024)
- [ ] JWT validation (aguarda Keycloak)

---

### 1.5 Implementar Keycloak (Auth/Identity)
**Objetivo:** Centralizar autenticação com SSO, LDAP, e OAuth2.

**Tarefas:**
- [ ] Adicionar Keycloak ao `docker-compose.yml`
- [ ] Configurar realm para GT-Vision
- [ ] Configurar client para frontend (public)
- [ ] Configurar client para backend (confidential)
- [ ] Integrar com Kong JWT plugin
- [ ] Configurar roles: admin, operator, viewer
- [ ] (Opcional) Integrar com LDAP/AD

**docker-compose.yml:**
```yaml
keycloak:
  image: quay.io/keycloak/keycloak:23.0
  command: start-dev
  environment:
    KC_DB: postgres
    KC_DB_URL: jdbc:postgresql://postgres_db:5432/keycloak
    KC_DB_USERNAME: ${POSTGRES_USER}
    KC_DB_PASSWORD: ${POSTGRES_PASSWORD}
    KEYCLOAK_ADMIN: admin
    KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_ADMIN_PASSWORD}
    KC_PROXY: edge
    KC_HOSTNAME_STRICT: false
  ports:
    - "8080:8080"
  depends_on:
    - postgres_db
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8080/health/ready"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Validação:**
- [ ] Keycloak Admin Console acessível
- [ ] Realm GT-Vision criado
- [ ] Clients configurados
- [ ] Login flow funcionando
- [ ] Tokens JWT sendo validados pelo Kong

---

## 📋 FASE 2: BACKEND & SERVIÇO DE IA (Semana 2-3)

### 2.1 Criar Serviço de IA com FastAPI (GPU Workers + AWS Rekognition)
**Objetivo:** Serviço dedicado de alta disponibilidade para detecção com suporte híbrido (GPU local ou AWS).

**Modos de Operação:**
| Modo | Onde Roda | Modelos | Custo | Latência |
|------|-----------|---------|-------|----------|
| **GPU Local** | On-premise / EC2 GPU | YOLO + TensorFlow | Fixo (hardware) | ~50ms |
| **AWS Rekognition** | EC2 t3/c5 + API AWS | Rekognition API | Pay-per-use | ~200ms |
| **Híbrido** | Ambos | Fallback automático | Otimizado | Variável |

**Estrutura:**
```
ai_service/
├── Dockerfile.gpu           # Para GPU workers locais
├── Dockerfile.cpu           # Para EC2 com Rekognition
├── requirements.txt
├── requirements-aws.txt     # Boto3, etc
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings (AI_BACKEND: gpu|aws|hybrid)
│   ├── providers/           # Abstração de providers de IA
│   │   ├── __init__.py
│   │   ├── base.py          # Interface base
│   │   ├── gpu_provider.py  # YOLO + TensorFlow local
│   │   ├── aws_provider.py  # AWS Rekognition
│   │   └── hybrid_provider.py # Fallback automático
│   ├── models/
│   │   ├── __init__.py
│   │   ├── yolo_detector.py   # YOLOv8/v11
│   │   └── tf_classifier.py   # TensorFlow models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── detection.py       # /detect endpoint
│   │   ├── health.py          # /health endpoint
│   │   └── batch.py           # /batch endpoint
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── frame_grabber.py   # Captura frames do MediaMTX
│   │   └── processor.py       # Pipeline de processamento
│   └── utils/
│       ├── __init__.py
│       ├── gpu_utils.py       # CUDA management
│       ├── aws_utils.py       # AWS helpers
│       └── metrics.py         # Prometheus metrics
├── models/                    # Model weights (apenas GPU mode)
│   ├── yolov8n.pt
│   ├── yolov8s.pt
│   └── custom_lpr.pt
├── terraform/                 # IaC para EC2 workers
│   ├── main.tf
│   ├── variables.tf
│   └── ec2-workers.tf
└── tests/
    └── test_detection.py
```

**Tarefas:**

**Core:**
- [ ] Criar `ai_service/Dockerfile.gpu` com CUDA 12.x (workers GPU)
- [ ] Criar `ai_service/Dockerfile.cpu` para EC2 com Rekognition
- [ ] Implementar `main.py` com FastAPI + Uvicorn
- [ ] Implementar interface base `providers/base.py`
- [ ] Implementar endpoint `/detect` (single frame)
- [ ] Implementar endpoint `/batch` (múltiplos frames)
- [ ] Implementar endpoint `/health` com status do provider
- [ ] Adicionar métricas Prometheus
- [ ] Configurar auto-scaling com réplicas

**GPU Provider (On-Premise / EC2 GPU):**
- [ ] Implementar `providers/gpu_provider.py`
- [ ] Implementar detector YOLO com batch processing
- [ ] Implementar detector TensorFlow para LPR
- [ ] Gerenciamento de memória GPU

**AWS Provider (EC2 + Rekognition):**
- [ ] Implementar `providers/aws_provider.py`
- [ ] Integrar AWS Rekognition DetectLabels
- [ ] Integrar AWS Rekognition DetectText (para placas)
- [ ] Integrar AWS Rekognition DetectFaces (opcional)
- [ ] Implementar retry logic com exponential backoff
- [ ] Configurar AWS credentials via IAM Role (EC2)

**Híbrido:**
- [ ] Implementar `providers/hybrid_provider.py`
- [ ] Lógica de fallback (GPU → AWS se GPU falhar)
- [ ] Load balancing entre providers
- [ ] Circuit breaker para AWS (evitar custos em falhas)

**Infraestrutura AWS:**
- [ ] Criar Terraform para EC2 workers
- [ ] Configurar Auto Scaling Group
- [ ] Configurar IAM Role com permissões Rekognition
- [ ] Configurar VPC endpoints para Rekognition (reduz latência)

**Dockerfile.gpu (GPU Workers Locais/EC2 GPU):**
```dockerfile
FROM nvidia/cuda:12.2-cudnn8-runtime-ubuntu22.04

WORKDIR /app

# Instalar Python e dependências
RUN apt-get update && apt-get install -y \
    python3.11 python3-pip libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app/ ./app/
COPY models/ ./models/

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0
ENV AI_BACKEND=gpu

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Rodar com múltiplos workers
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

**Dockerfile.cpu (EC2 com AWS Rekognition):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências mínimas
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python (sem CUDA)
COPY requirements-aws.txt .
RUN pip install --no-cache-dir -r requirements-aws.txt

# Copiar código (sem modelos pesados)
COPY app/ ./app/

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV AI_BACKEND=aws
ENV AWS_DEFAULT_REGION=us-east-1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Rodar com mais workers (CPU é barato)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**requirements.txt (GPU mode):**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
ultralytics==8.1.0
torch==2.2.0
torchvision==0.17.0
tensorflow==2.15.0
opencv-python-headless==4.9.0.80
numpy==1.26.3
httpx==0.26.0
prometheus-client==0.19.0
python-multipart==0.0.6
Pillow==10.2.0
redis==5.0.1
```

**requirements-aws.txt (AWS Rekognition mode):**
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
boto3==1.34.0
botocore==1.34.0
opencv-python-headless==4.9.0.80
numpy==1.26.3
httpx==0.26.0
prometheus-client==0.19.0
python-multipart==0.0.6
Pillow==10.2.0
redis==5.0.1
aioboto3==12.0.0
```

**app/main.py:**
```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.config import settings
from app.providers.base import AIProvider
from app.providers.gpu_provider import GPUProvider
from app.providers.aws_provider import AWSProvider
from app.providers.hybrid_provider import HybridProvider

# Métricas Prometheus
REQUESTS_TOTAL = Counter('ai_requests_total', 'Total de requisições', ['endpoint', 'status', 'provider'])
INFERENCE_TIME = Histogram('ai_inference_seconds', 'Tempo de inferência', ['provider'])

# Provider de IA (carregado na inicialização)
ai_provider: AIProvider = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Carrega provider de IA baseado na configuração."""
    global ai_provider
    
    print(f"🚀 Inicializando AI Provider: {settings.AI_BACKEND}")
    
    if settings.AI_BACKEND == "gpu":
        ai_provider = GPUProvider(
            yolo_model=settings.YOLO_MODEL_PATH,
            lpr_model=settings.LPR_MODEL_PATH,
            device=settings.GPU_DEVICE,
            confidence=settings.CONFIDENCE_THRESHOLD
        )
    elif settings.AI_BACKEND == "aws":
        ai_provider = AWSProvider(
            region=settings.AWS_REGION,
            min_confidence=settings.CONFIDENCE_THRESHOLD * 100  # AWS usa 0-100
        )
    elif settings.AI_BACKEND == "hybrid":
        ai_provider = HybridProvider(
            primary=GPUProvider(...),
            fallback=AWSProvider(...),
            fallback_on_error=True
        )
    else:
        raise ValueError(f"AI_BACKEND inválido: {settings.AI_BACKEND}")
    
    await ai_provider.initialize()
    print(f"✅ AI Provider '{settings.AI_BACKEND}' inicializado!")
    
    yield
    
    # Cleanup
    print("🛑 Desligando AI Provider...")
    await ai_provider.shutdown()

app = FastAPI(
    title="GT-Vision AI Service",
    description="Serviço de detecção com suporte a GPU local e AWS Rekognition",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/metrics")
async def metrics():
    """Endpoint para Prometheus."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health():
    """Health check com status do provider."""
    status = await ai_provider.health_check()
    return {
        "status": "healthy" if status["ok"] else "unhealthy",
        "provider": settings.AI_BACKEND,
        "details": status
    }

@app.post("/detect/frame")
async def detect_frame(
    file: UploadFile = File(...),
    camera_id: int = None,
    detect_plates: bool = True
):
    """
    Detecta objetos em um frame.
    Usa GPU local ou AWS Rekognition baseado na configuração.
    """
    try:
        contents = await file.read()
        
        with INFERENCE_TIME.labels(provider=settings.AI_BACKEND).time():
            detections = await ai_provider.detect(
                image_bytes=contents,
                detect_text=detect_plates
            )
        
        REQUESTS_TOTAL.labels(
            endpoint='detect', 
            status='success',
            provider=settings.AI_BACKEND
        ).inc()
        
        return {
            "camera_id": camera_id,
            "provider": settings.AI_BACKEND,
            "detections": detections,
            "count": len(detections)
        }
        
    except Exception as e:
        REQUESTS_TOTAL.labels(
            endpoint='detect', 
            status='error',
            provider=settings.AI_BACKEND
        ).inc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch/detect")
async def batch_detect(
    files: list[UploadFile] = File(...),
    camera_ids: list[int] = None
):
    """Processa múltiplos frames em batch."""
    images = [await f.read() for f in files]
    
    with INFERENCE_TIME.labels(provider=settings.AI_BACKEND).time():
        results = await ai_provider.detect_batch(images)
    
    return {
        "provider": settings.AI_BACKEND,
        "results": [
            {"camera_id": cid, "detections": dets}
            for cid, dets in zip(camera_ids or range(len(results)), results)
        ]
    }
```

**app/providers/base.py:**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class AIProvider(ABC):
    """Interface base para providers de IA."""
    
    @abstractmethod
    async def initialize(self) -> None:
        """Inicializa o provider (carrega modelos, conecta APIs, etc)."""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup do provider."""
        pass
    
    @abstractmethod
    async def detect(
        self, 
        image_bytes: bytes, 
        detect_text: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Detecta objetos em uma imagem.
        
        Returns:
            Lista de detecções: [{"class": str, "confidence": float, "bbox": [x1,y1,x2,y2], "text": str|None}]
        """
        pass
    
    @abstractmethod
    async def detect_batch(
        self, 
        images: List[bytes]
    ) -> List[List[Dict[str, Any]]]:
        """Detecta objetos em múltiplas imagens."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Retorna status de saúde do provider."""
        pass
```

**app/providers/aws_provider.py:**
```python
import aioboto3
from typing import List, Dict, Any
from app.providers.base import AIProvider
import io

class AWSProvider(AIProvider):
    """Provider usando AWS Rekognition."""
    
    def __init__(self, region: str = "us-east-1", min_confidence: float = 50.0):
        self.region = region
        self.min_confidence = min_confidence
        self.session = None
        self.client = None
    
    async def initialize(self) -> None:
        self.session = aioboto3.Session()
        # Cliente será criado por requisição (connection pooling do aioboto3)
        print(f"AWS Provider inicializado (região: {self.region})")
    
    async def shutdown(self) -> None:
        pass  # aioboto3 gerencia conexões automaticamente
    
    async def detect(
        self, 
        image_bytes: bytes, 
        detect_text: bool = False
    ) -> List[Dict[str, Any]]:
        detections = []
        
        async with self.session.client('rekognition', region_name=self.region) as client:
            # Detectar objetos/labels
            labels_response = await client.detect_labels(
                Image={'Bytes': image_bytes},
                MinConfidence=self.min_confidence,
                Features=['GENERAL_LABELS']
            )
            
            for label in labels_response.get('Labels', []):
                for instance in label.get('Instances', []):
                    bbox = instance.get('BoundingBox', {})
                    detections.append({
                        "class": label['Name'].lower(),
                        "confidence": label['Confidence'] / 100,
                        "bbox": self._convert_bbox(bbox),
                        "source": "rekognition"
                    })
            
            # Detectar texto (placas)
            if detect_text:
                text_response = await client.detect_text(
                    Image={'Bytes': image_bytes}
                )
                
                for text in text_response.get('TextDetections', []):
                    if text['Type'] == 'LINE' and text['Confidence'] > self.min_confidence:
                        bbox = text.get('Geometry', {}).get('BoundingBox', {})
                        detections.append({
                            "class": "plate",
                            "confidence": text['Confidence'] / 100,
                            "bbox": self._convert_bbox(bbox),
                            "text": text['DetectedText'],
                            "source": "rekognition"
                        })
        
        return detections
    
    async def detect_batch(
        self, 
        images: List[bytes]
    ) -> List[List[Dict[str, Any]]]:
        """Processa múltiplas imagens em paralelo."""
        import asyncio
        tasks = [self.detect(img, detect_text=True) for img in images]
        return await asyncio.gather(*tasks)
    
    async def health_check(self) -> Dict[str, Any]:
        try:
            async with self.session.client('rekognition', region_name=self.region) as client:
                # Chamada leve para verificar conectividade
                await client.describe_projects(MaxResults=1)
            return {"ok": True, "provider": "aws", "region": self.region}
        except Exception as e:
            return {"ok": False, "provider": "aws", "error": str(e)}
    
    def _convert_bbox(self, aws_bbox: dict) -> List[float]:
        """Converte bbox AWS (normalizado) para [x1, y1, x2, y2]."""
        if not aws_bbox:
            return [0, 0, 0, 0]
        # AWS retorna: Left, Top, Width, Height (0-1)
        # Convertemos para: x1, y1, x2, y2 (0-1)
        return [
            aws_bbox.get('Left', 0),
            aws_bbox.get('Top', 0),
            aws_bbox.get('Left', 0) + aws_bbox.get('Width', 0),
            aws_bbox.get('Top', 0) + aws_bbox.get('Height', 0)
        ]
```

**app/providers/hybrid_provider.py:**
```python
from typing import List, Dict, Any
from app.providers.base import AIProvider
import asyncio

class HybridProvider(AIProvider):
    """Provider híbrido com fallback automático."""
    
    def __init__(
        self, 
        primary: AIProvider, 
        fallback: AIProvider,
        fallback_on_error: bool = True,
        fallback_on_timeout: float = 5.0
    ):
        self.primary = primary
        self.fallback = fallback
        self.fallback_on_error = fallback_on_error
        self.fallback_on_timeout = fallback_on_timeout
        self.primary_failures = 0
        self.circuit_open = False
    
    async def initialize(self) -> None:
        await asyncio.gather(
            self.primary.initialize(),
            self.fallback.initialize()
        )
        print("Hybrid Provider inicializado (primary + fallback)")
    
    async def shutdown(self) -> None:
        await asyncio.gather(
            self.primary.shutdown(),
            self.fallback.shutdown()
        )
    
    async def detect(
        self, 
        image_bytes: bytes, 
        detect_text: bool = False
    ) -> List[Dict[str, Any]]:
        # Circuit breaker: se muitas falhas, vai direto pro fallback
        if self.circuit_open:
            return await self.fallback.detect(image_bytes, detect_text)
        
        try:
            result = await asyncio.wait_for(
                self.primary.detect(image_bytes, detect_text),
                timeout=self.fallback_on_timeout
            )
            self.primary_failures = 0  # Reset on success
            return result
            
        except (asyncio.TimeoutError, Exception) as e:
            self.primary_failures += 1
            
            # Abrir circuit breaker após 5 falhas consecutivas
            if self.primary_failures >= 5:
                self.circuit_open = True
                # Agendar fechamento do circuit em 60s
                asyncio.create_task(self._close_circuit_after(60))
            
            if self.fallback_on_error:
                print(f"Primary falhou ({e}), usando fallback")
                return await self.fallback.detect(image_bytes, detect_text)
            raise
    
    async def _close_circuit_after(self, seconds: float):
        await asyncio.sleep(seconds)
        self.circuit_open = False
        self.primary_failures = 0
        print("Circuit breaker fechado, primary reabilitado")
    
    async def detect_batch(
        self, 
        images: List[bytes]
    ) -> List[List[Dict[str, Any]]]:
        tasks = [self.detect(img, detect_text=True) for img in images]
        return await asyncio.gather(*tasks)
    
    async def health_check(self) -> Dict[str, Any]:
        primary_health = await self.primary.health_check()
        fallback_health = await self.fallback.health_check()
        
        return {
            "ok": primary_health["ok"] or fallback_health["ok"],
            "provider": "hybrid",
            "circuit_open": self.circuit_open,
            "primary": primary_health,
            "fallback": fallback_health
        }
```

**app/models/yolo_detector.py:**
```python
from ultralytics import YOLO
import numpy as np
import cv2
from io import BytesIO
from PIL import Image

class YOLODetector:
    def __init__(self, model_path: str, device: str = "cuda", confidence: float = 0.5):
        self.model = YOLO(model_path)
        self.model.to(device)
        self.confidence = confidence
        self.device = device
    
    def detect(self, image_bytes: bytes) -> list:
        """Detecta objetos na imagem."""
        # Converter bytes para numpy
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Inferência
        results = self.model(img, conf=self.confidence, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                detection = {
                    "class": result.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "bbox": box.xyxy[0].tolist(),  # [x1, y1, x2, y2]
                }
                detections.append(detection)
        
        return detections
    
    def detect_batch(self, images: list[bytes]) -> list[list]:
        """Detecta objetos em múltiplas imagens."""
        # Converter todos para numpy
        imgs = []
        for img_bytes in images:
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            imgs.append(img)
        
        # Batch inference
        results = self.model(imgs, conf=self.confidence, verbose=False)
        
        all_detections = []
        for result in results:
            detections = []
            for box in result.boxes:
                detection = {
                    "class": result.names[int(box.cls)],
                    "confidence": float(box.conf),
                    "bbox": box.xyxy[0].tolist(),
                }
                detections.append(detection)
            all_detections.append(detections)
        
        return all_detections
```

**app/workers/frame_grabber.py:**
```python
import asyncio
import httpx
from typing import Optional
import redis.asyncio as redis
from app.config import settings

class FrameGrabber:
    """Captura frames do MediaMTX para processamento."""
    
    def __init__(self):
        self.mediamtx_api = settings.MEDIAMTX_API_URL
        self.redis = redis.from_url(settings.REDIS_URL)
        self.http_client = httpx.AsyncClient(timeout=5.0)
    
    async def grab_frame(self, camera_id: int) -> Optional[bytes]:
        """Captura um frame de uma câmera via MediaMTX API."""
        try:
            # Usar snapshot API do MediaMTX
            url = f"{self.mediamtx_api}/v3/paths/cam_{camera_id}/snapshot"
            response = await self.http_client.get(url)
            
            if response.status_code == 200:
                return response.content
            return None
            
        except Exception as e:
            print(f"Erro ao capturar frame da camera {camera_id}: {e}")
            return None
    
    async def grab_frames_batch(self, camera_ids: list[int]) -> dict[int, bytes]:
        """Captura frames de múltiplas câmeras em paralelo."""
        tasks = {cid: self.grab_frame(cid) for cid in camera_ids}
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        frames = {}
        for cid, result in zip(tasks.keys(), results):
            if isinstance(result, bytes):
                frames[cid] = result
        
        return frames
    
    async def start_continuous_grabbing(self, camera_ids: list[int], fps: float = 1.0):
        """Inicia captura contínua de frames para processamento."""
        interval = 1.0 / fps
        
        while True:
            frames = await self.grab_frames_batch(camera_ids)
            
            # Publicar frames no Redis para workers processarem
            for camera_id, frame in frames.items():
                await self.redis.lpush(
                    f"frames:queue:{camera_id}",
                    frame
                )
                # Manter apenas últimos 10 frames na fila
                await self.redis.ltrim(f"frames:queue:{camera_id}", 0, 9)
            
            await asyncio.sleep(interval)
```

**docker-compose.yml (GPU Workers Locais):**
```yaml
ai-service-gpu:
  build:
    context: ./ai_service
    dockerfile: Dockerfile.gpu
  deploy:
    mode: replicated
    replicas: 2  # CONFIGURÁVEL: Alta disponibilidade
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  environment:
    - AI_BACKEND=gpu
    - CUDA_VISIBLE_DEVICES=0
    - GPU_DEVICE=cuda:0
    - YOLO_MODEL_PATH=/app/models/yolov8s.pt
    - LPR_MODEL_PATH=/app/models/custom_lpr.pt
    - CONFIDENCE_THRESHOLD=0.5
    - REDIS_URL=redis://redis:6379/0
    - MEDIAMTX_API_URL=http://mediamtx:9997
  volumes:
    - ./ai_service/models:/app/models:ro
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
  depends_on:
    - redis
    - mediamtx
  networks:
    - gt-vision-network
```

**docker-compose.aws.yml (EC2 Workers com Rekognition):**
```yaml
# Para usar em EC2: docker-compose -f docker-compose.yml -f docker-compose.aws.yml up
ai-service-aws:
  build:
    context: ./ai_service
    dockerfile: Dockerfile.cpu
  deploy:
    mode: replicated
    replicas: 4  # Mais réplicas (CPU é barato)
  environment:
    - AI_BACKEND=aws
    - AWS_DEFAULT_REGION=${AWS_REGION:-us-east-1}
    - CONFIDENCE_THRESHOLD=0.5
    - REDIS_URL=redis://redis:6379/0
    - MEDIAMTX_API_URL=http://mediamtx:9997
    # Credenciais via IAM Role (recomendado) ou env vars
    # - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
    # - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
  depends_on:
    - redis
    - mediamtx
  networks:
    - gt-vision-network
```

**docker-compose.hybrid.yml (Modo Híbrido):**
```yaml
# Para usar modo híbrido: docker-compose -f docker-compose.yml -f docker-compose.hybrid.yml up
ai-service-hybrid:
  build:
    context: ./ai_service
    dockerfile: Dockerfile.gpu  # Precisa de GPU para primary
  deploy:
    mode: replicated
    replicas: 2
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  environment:
    - AI_BACKEND=hybrid
    - CUDA_VISIBLE_DEVICES=0
    - GPU_DEVICE=cuda:0
    - YOLO_MODEL_PATH=/app/models/yolov8s.pt
    - LPR_MODEL_PATH=/app/models/custom_lpr.pt
    - AWS_DEFAULT_REGION=${AWS_REGION:-us-east-1}
    - CONFIDENCE_THRESHOLD=0.5
    - FALLBACK_TIMEOUT=5.0
    - REDIS_URL=redis://redis:6379/0
    - MEDIAMTX_API_URL=http://mediamtx:9997
  volumes:
    - ./ai_service/models:/app/models:ro
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
  networks:
    - gt-vision-network
```

**Terraform para EC2 Workers (terraform/ec2-workers.tf):**
```hcl
# Variáveis
variable "aws_region" {
  default = "us-east-1"
}

variable "instance_type" {
  default = "c5.xlarge"  # 4 vCPU, 8GB RAM - bom para Rekognition
}

variable "min_workers" {
  default = 2
}

variable "max_workers" {
  default = 10
}

# IAM Role para Rekognition
resource "aws_iam_role" "ai_worker_role" {
  name = "gt-vision-ai-worker-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "rekognition_policy" {
  name = "rekognition-access"
  role = aws_iam_role.ai_worker_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "rekognition:DetectLabels",
          "rekognition:DetectText",
          "rekognition:DetectFaces",
          "rekognition:DescribeProjects"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "ai_worker_profile" {
  name = "gt-vision-ai-worker-profile"
  role = aws_iam_role.ai_worker_role.name
}

# Launch Template
resource "aws_launch_template" "ai_worker" {
  name_prefix   = "gt-vision-ai-worker-"
  image_id      = data.aws_ami.amazon_linux_2.id
  instance_type = var.instance_type

  iam_instance_profile {
    name = aws_iam_instance_profile.ai_worker_profile.name
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    systemctl start docker
    systemctl enable docker
    
    # Login no ECR (se usando)
    # aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com
    
    # Rodar AI Service
    docker run -d \
      --name ai-service \
      --restart always \
      -p 8000:8000 \
      -e AI_BACKEND=aws \
      -e AWS_DEFAULT_REGION=${var.aws_region} \
      -e REDIS_URL=${redis_url} \
      -e MEDIAMTX_API_URL=${mediamtx_url} \
      gt-vision/ai-service:latest
  EOF
  )

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "gt-vision-ai-worker"
    }
  }
}

# Auto Scaling Group
resource "aws_autoscaling_group" "ai_workers" {
  name                = "gt-vision-ai-workers"
  desired_capacity    = var.min_workers
  min_size            = var.min_workers
  max_size            = var.max_workers
  vpc_zone_identifier = var.subnet_ids
  target_group_arns   = [aws_lb_target_group.ai_workers.arn]

  launch_template {
    id      = aws_launch_template.ai_worker.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "gt-vision-ai-worker"
    propagate_at_launch = true
  }
}

# Auto Scaling Policy baseado em CPU
resource "aws_autoscaling_policy" "scale_up" {
  name                   = "scale-up"
  scaling_adjustment     = 2
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.ai_workers.name
}

resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "ai-workers-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Average"
  threshold           = 70

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.ai_workers.name
  }

  alarm_actions = [aws_autoscaling_policy.scale_up.arn]
}

# Load Balancer para AI Workers
resource "aws_lb" "ai_workers" {
  name               = "gt-vision-ai-lb"
  internal           = true
  load_balancer_type = "application"
  subnets            = var.subnet_ids
}

resource "aws_lb_target_group" "ai_workers" {
  name     = "gt-vision-ai-tg"
  port     = 8000
  protocol = "HTTP"
  vpc_id   = var.vpc_id

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
  }
}

resource "aws_lb_listener" "ai_workers" {
  load_balancer_arn = aws_lb.ai_workers.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ai_workers.arn
  }
}

# Output
output "ai_lb_dns" {
  value = aws_lb.ai_workers.dns_name
}
```

**Validação:**
- [ ] AI Service rodando (GPU ou AWS mode)
- [ ] Endpoint /detect funcionando
- [ ] Endpoint /batch processando múltiplos frames
- [ ] Métricas expostas em /metrics
- [ ] Alta disponibilidade com 2+ réplicas
- [ ] **GPU Mode:** Latência <100ms por frame
- [ ] **AWS Mode:** Latência <300ms por frame
- [ ] **Hybrid Mode:** Fallback funcionando, circuit breaker testado
- [ ] **AWS:** Auto Scaling respondendo a carga
- [ ] **AWS:** IAM Role com permissões corretas

---

### 2.1.1 Custos Estimados (AWS Rekognition)

| Operação | Preço (us-east-1) | 250 câmeras @ 1 FPS |
|----------|-------------------|---------------------|
| DetectLabels | $0.001/imagem | $21,600/mês |
| DetectText | $0.001/imagem | $21,600/mês |
| **Total** | - | **~$43,200/mês** |

**Otimizações de custo:**
- Reduzir FPS para 0.5 (1 frame a cada 2s): **$21,600/mês**
- Usar GPU local para câmeras críticas, AWS para resto
- Implementar detecção de movimento antes de enviar para IA
- Usar cache de resultados para frames similares

**Comparativo GPU Local vs AWS:**
| Aspecto | GPU Local (RTX 4090) | AWS Rekognition |
|---------|---------------------|-----------------|
| Custo inicial | ~$2,000/GPU | $0 |
| Custo mensal | ~$50 (energia) | ~$43,200 (250 cam) |
| Latência | ~50ms | ~200ms |
| Escalabilidade | Limitada | Ilimitada |
| Manutenção | Alta | Zero |
| Customização | Total (modelos custom) | Limitada |

**Recomendação:** Modo híbrido - GPU para câmeras críticas (LPR), AWS para resto.

---

### 2.2 Otimizar Ingestão de Detecções (Gateway FastAPI)
**Objetivo:** Suportar >1000 detecções/segundo sem perda.

**Tarefas:**
- [ ] Implementar batch insert no `gateway/main.py`
- [ ] Adicionar fila Redis para buffer (se DB lento)
- [ ] Usar connection pooling no PostgreSQL (PgBouncer)
- [ ] Adicionar índices no banco (camera_id, timestamp)
- [ ] Implementar rate limiting por câmera (evitar spam)
- [ ] Integrar com AI Service para receber detecções

**Otimização de ingestão:**
```python
from fastapi import FastAPI, BackgroundTasks
from redis import asyncio as aioredis
import asyncpg
from datetime import datetime
import json

# CONFIGURÁVEL: BATCH_SIZE para ajustar throughput vs latência
BATCH_SIZE = 100
BATCH_TIMEOUT = 1.0  # segundos

app = FastAPI()
redis_client = None
db_pool = None
detection_buffer = []

@app.on_event("startup")
async def startup():
    global redis_client, db_pool
    redis_client = await aioredis.from_url("redis://redis:6379/0")
    db_pool = await asyncpg.create_pool(
        dsn="postgresql://user:pass@pgbouncer:6432/gtvision",
        min_size=10,
        max_size=50
    )

@app.post("/fast-api/ingest/detection")
async def ingest_detection(detection: dict, background_tasks: BackgroundTasks):
    """Recebe detecções do AI Service."""
    # Adicionar timestamp
    detection['received_at'] = datetime.utcnow().isoformat()
    
    # Buffer em memória
    detection_buffer.append(detection)
    
    if len(detection_buffer) >= BATCH_SIZE:
        # Flush assíncrono
        batch = detection_buffer.copy()
        detection_buffer.clear()
        background_tasks.add_task(flush_to_db, batch)
    
    # Publicar para WebSocket subscribers
    await redis_client.publish(
        f"detections:{detection['camera_id']}",
        json.dumps(detection)
    )
    
    return {"status": "queued", "buffer_size": len(detection_buffer)}

async def flush_to_db(batch: list):
    """Batch insert no PostgreSQL."""
    async with db_pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO detections (camera_id, class, confidence, bbox, plate, timestamp)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            [
                (d['camera_id'], d['class'], d['confidence'], 
                 json.dumps(d['bbox']), d.get('plate'), d['timestamp'])
                for d in batch
            ]
        )
```

**Validação:**
- [ ] Teste de carga: 1000 req/s com Locust
- [ ] Latência p95 <50ms
- [ ] Zero perda de dados

---

### 2.3 Implementar PgBouncer (Connection Pooling)
**Objetivo:** Reduzir overhead de conexões ao PostgreSQL.

**Tarefas:**
- [ ] Adicionar serviço `pgbouncer` ao `docker-compose.yml`
- [ ] Configurar pool de 100 conexões
- [ ] Apontar Django e Gateway para PgBouncer (porta 6432)
- [ ] Configurar modo `transaction` (melhor performance)

**docker-compose.yml:**
```yaml
pgbouncer:
  image: pgbouncer/pgbouncer:latest
  environment:
    - DATABASES_HOST=postgres_db
    - DATABASES_PORT=5432
    - DATABASES_USER=${POSTGRES_USER}
    - DATABASES_PASSWORD=${POSTGRES_PASSWORD}
    - DATABASES_DBNAME=${POSTGRES_DB}
    - PGBOUNCER_POOL_MODE=transaction
    - PGBOUNCER_MAX_CLIENT_CONN=1000    # CONFIGURÁVEL
    - PGBOUNCER_DEFAULT_POOL_SIZE=25    # CONFIGURÁVEL
  ports:
    - "6432:6432"
  depends_on:
    - postgres_db
  healthcheck:
    test: ["CMD", "pg_isready", "-h", "localhost", "-p", "6432"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Validação:**
- [ ] Django conecta via PgBouncer
- [ ] Verificar `SHOW POOLS;` no PgBouncer
- [ ] Latência de queries mantida ou melhorada

---

### 2.4 Implementar MinIO (Object Storage)
**Objetivo:** Armazenar frames, gravações e evidências de forma escalável.

**Tarefas:**
- [ ] Adicionar MinIO ao `docker-compose.yml`
- [ ] Configurar buckets: frames, recordings, evidence
- [ ] Configurar lifecycle policy (retenção 7 dias para frames)
- [ ] Integrar AI Service para salvar frames processados
- [ ] Configurar replicação (opcional, para HA)

**docker-compose.yml:**
```yaml
minio:
  image: minio/minio:latest
  command: server /data --console-address ":9001"
  environment:
    - MINIO_ROOT_USER=${MINIO_ROOT_USER}
    - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD}
  volumes:
    - minio_data:/data
  ports:
    - "9000:9000"   # API
    - "9001:9001"   # Console
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
    interval: 30s
    timeout: 10s
    retries: 3
```

**Configuração de buckets (script de inicialização):**
```bash
#!/bin/bash
# scripts/init-minio.sh

mc alias set myminio http://minio:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Criar buckets
mc mb myminio/frames --ignore-existing
mc mb myminio/recordings --ignore-existing
mc mb myminio/evidence --ignore-existing

# Lifecycle policy - deletar frames após 7 dias
mc ilm rule add myminio/frames --expire-days 7

# Lifecycle policy - deletar recordings após 30 dias
mc ilm rule add myminio/recordings --expire-days 30

echo "MinIO buckets configurados!"
```

**Validação:**
- [ ] MinIO Console acessível (:9001)
- [ ] Buckets criados
- [ ] Lifecycle policies funcionando
- [ ] AI Service salvando frames

---

### 2.5 Otimizar Queries Django (Gargalos Conhecidos)
**Objetivo:** Reduzir latência de listagens e dashboards.

**Tarefas:**
- [ ] Adicionar `select_related()` e `prefetch_related()` em ViewSets
- [ ] Criar índices compostos no PostgreSQL
- [ ] Usar `only()` e `defer()` para reduzir campos carregados
- [ ] Implementar paginação cursor-based para listas grandes
- [ ] Cachear queries pesadas no Redis (TTL 5s)

**Índices críticos:**
```sql
-- CONFIGURÁVEL: Ajustar conforme queries mais frequentes
CREATE INDEX CONCURRENTLY idx_deteccoes_camera_ts 
  ON deteccoes(camera_id, timestamp DESC);

CREATE INDEX CONCURRENTLY idx_deteccoes_ts 
  ON deteccoes(timestamp DESC) 
  WHERE timestamp > NOW() - INTERVAL '7 days';

CREATE INDEX CONCURRENTLY idx_cameras_ativa 
  ON cameras(ativa) 
  WHERE ativa = true;
```

**Validação:**
- [ ] `EXPLAIN ANALYZE` em queries lentas
- [ ] Latência de listagem <100ms
- [ ] Dashboard carrega em <500ms

---

## 📋 FASE 3: FRONTEND (Semana 3)

### 3.1 Otimizar Bundle Size (Code Splitting)
**Objetivo:** Reduzir bundle de >2MB para <500KB (gzipped).

**Tarefas:**
- [ ] Analisar bundle com `npm run build -- --analyze`
- [ ] Implementar lazy loading de rotas
- [ ] Remover bibliotecas não utilizadas
- [ ] Substituir bibliotecas pesadas por alternativas leves
- [ ] Configurar tree-shaking no Vite

**Otimizações:**
```typescript
// Lazy loading de páginas
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Cameras = lazy(() => import('./pages/Cameras'));

// Remover libs pesadas
// ❌ moment.js (500KB) → ✅ date-fns (10KB)
// ❌ lodash completo → ✅ lodash-es (tree-shakeable)
```

**Validação:**
- [ ] Bundle principal <200KB (gzipped)
- [ ] Chunks de rotas <100KB cada
- [ ] Lighthouse score >90

---

### 3.2 Otimizar Player de Vídeo (HLS.js)
**Objetivo:** Player leve com overlay de detecções via Canvas.

**Tarefas:**
- [ ] Usar HLS.js nativo (sem wrappers pesados)
- [ ] Implementar Canvas overlay para bounding boxes
- [ ] Adicionar fallback para WebRTC (baixa latência)
- [ ] Implementar lazy loading de players (só carrega quando visível)
- [ ] Otimizar re-renders com `React.memo()`

**Player otimizado:**
```typescript
// CONFIGURÁVEL: HLS_BUFFER_SIZE para ajustar latência
const HLS_CONFIG = {
  maxBufferLength: 10,        // CONFIGURÁVEL: Menor = menos latência
  maxMaxBufferLength: 20,
  liveSyncDuration: 3,
};

const VideoPlayer = React.memo(({ cameraId }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Renderiza bounding boxes no Canvas (não no DOM)
  const drawDetections = useCallback((detections) => {
    const ctx = canvasRef.current?.getContext('2d');
    // ... desenha retângulos
  }, []);
  
  return (
    <>
      <video ref={videoRef} />
      <canvas ref={canvasRef} />
    </>
  );
});
```

**Validação:**
- [ ] Player carrega em <1s
- [ ] Overlay de detecções sem lag
- [ ] Suporta 16 streams simultâneos sem travar

---

### 3.3 Implementar Virtual Scrolling (Listas Grandes)
**Objetivo:** Renderizar apenas itens visíveis em listas de câmeras/detecções.

**Tarefas:**
- [ ] Instalar `@tanstack/react-virtual`
- [ ] Implementar em lista de câmeras
- [ ] Implementar em lista de detecções
- [ ] Adicionar skeleton loading

**Validação:**
- [ ] Lista de 1000 itens renderiza instantaneamente
- [ ] Scroll suave (60fps)

---

## 📋 FASE 4: OBSERVABILIDADE COMPLETA (Semana 4)

### 4.1 Implementar Stack de Observabilidade Completa
**Objetivo:** Métricas, Logs e Tracing centralizados.

**Componentes:**
- **Prometheus**: Métricas
- **Grafana**: Dashboards
- **Loki**: Logs agregados
- **Jaeger**: Distributed tracing
- **Alertmanager**: Alertas → PagerDuty/Slack

**Tarefas:**
- [ ] Adicionar stack completa ao `docker-compose.yml`
- [ ] Configurar exporters: node, postgres, redis, nginx
- [ ] Configurar Promtail para coletar logs
- [ ] Configurar Jaeger para tracing
- [ ] Criar dashboards Grafana
- [ ] Configurar alertas no Alertmanager

**docker-compose.yml:**
```yaml
# Prometheus
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  command:
    - '--config.file=/etc/prometheus/prometheus.yml'
    - '--storage.tsdb.path=/prometheus'
    - '--storage.tsdb.retention.time=15d'
  ports:
    - "9090:9090"

# Grafana
grafana:
  image: grafana/grafana:latest
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}
    - GF_USERS_ALLOW_SIGN_UP=false
  volumes:
    - grafana_data:/var/lib/grafana
    - ./grafana/provisioning:/etc/grafana/provisioning
    - ./grafana/dashboards:/var/lib/grafana/dashboards
  ports:
    - "3001:3000"
  depends_on:
    - prometheus
    - loki

# Loki (Logs)
loki:
  image: grafana/loki:latest
  volumes:
    - ./loki/loki-config.yml:/etc/loki/local-config.yaml
    - loki_data:/loki
  ports:
    - "3100:3100"
  command: -config.file=/etc/loki/local-config.yaml

# Promtail (Log collector)
promtail:
  image: grafana/promtail:latest
  volumes:
    - ./promtail/promtail-config.yml:/etc/promtail/config.yml
    - /var/log:/var/log:ro
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
  command: -config.file=/etc/promtail/config.yml
  depends_on:
    - loki

# Jaeger (Tracing)
jaeger:
  image: jaegertracing/all-in-one:latest
  environment:
    - COLLECTOR_OTLP_ENABLED=true
  ports:
    - "16686:16686"  # UI
    - "4317:4317"    # OTLP gRPC
    - "4318:4318"    # OTLP HTTP

# Alertmanager
alertmanager:
  image: prom/alertmanager:latest
  volumes:
    - ./alertmanager/alertmanager.yml:/etc/alertmanager/alertmanager.yml
  ports:
    - "9093:9093"
  command:
    - '--config.file=/etc/alertmanager/alertmanager.yml'
```

**prometheus/prometheus.yml:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/rules/*.yml'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'ai-service'
    static_configs:
      - targets: ['ai-service:8000']
    metrics_path: /metrics

  - job_name: 'gateway'
    static_configs:
      - targets: ['gateway:8001']

  - job_name: 'django'
    static_configs:
      - targets: ['django:8000']
    metrics_path: /metrics

  - job_name: 'mediamtx'
    static_configs:
      - targets: ['mediamtx:9998']

  - job_name: 'kong'
    static_configs:
      - targets: ['kong:8001']
    metrics_path: /metrics

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

**alertmanager/alertmanager.yml:**
```yaml
global:
  slack_api_url: '${SLACK_WEBHOOK_URL}'

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'slack-notifications'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - channel: '#gt-vision-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
        severity: critical
```

**Validação:**
- [ ] Prometheus coletando métricas de todos serviços
- [ ] Grafana com dashboards funcionais
- [ ] Loki agregando logs
- [ ] Jaeger mostrando traces
- [ ] Alertas chegando no Slack

---

### 4.2 Testes de Carga (Locust)
**Objetivo:** Validar que sistema suporta 250 câmeras + 100 usuários.

**Tarefas:**
- [ ] Criar `tests/load/api_load.py` (Locust)
- [ ] Simular 100 usuários acessando dashboard
- [ ] Simular 1000 detecções/segundo
- [ ] Simular 50 streams simultâneos
- [ ] Medir latência p95, p99
- [ ] Identificar gargalos

**Cenários de teste:**
```python
# tests/load/locustfile.py
from locust import HttpUser, task, between, events
import random

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/api/analytics/dashboard/")
    
    @task(2)
    def list_cameras(self):
        self.client.get("/api/cameras/")
    
    @task(1)
    def view_detections(self):
        camera_id = random.randint(1, 250)
        self.client.get(f"/api/deteccoes/?camera_id={camera_id}")

class AIUser(HttpUser):
    """Simula carga no serviço de IA."""
    wait_time = between(0.5, 1)
    
    @task
    def detect_frame(self):
        with open("test_frame.jpg", "rb") as f:
            self.client.post(
                "/detect/frame",
                files={"file": f},
                data={"camera_id": random.randint(1, 250)}
            )
```

**Validação:**
- [ ] API: p95 <100ms, p99 <200ms
- [ ] AI Service: p95 <100ms por frame
- [ ] Ingestão: >1000 req/s sem erros
- [ ] Vídeo: latência <3s (HLS)
- [ ] Zero crashes ou timeouts

---

### 4.3 Testes de Resiliência
**Objetivo:** Sistema se recupera de falhas automaticamente.

**Tarefas:**
- [ ] Testar queda de PostgreSQL (failover para réplica)
- [ ] Testar queda de Redis (reconexão automática)
- [ ] Testar queda de MediaMTX (reconexão de câmeras)
- [ ] Testar queda de AI Service (load balancer redireciona)
- [ ] Testar queda de câmera (health check detecta)
- [ ] Testar sobrecarga (rate limiting funciona)

**Validação:**
- [ ] Downtime <30s em falhas de componentes
- [ ] Dados não são perdidos
- [ ] Alertas são disparados
- [ ] AI Service mantém disponibilidade com réplicas

---

## 📊 CHECKLIST FINAL (MVP Ready)

### Performance
- [ ] API: p95 <100ms
- [ ] AI Service (GPU): p95 <100ms por frame
- [ ] AI Service (AWS): p95 <300ms por frame
- [ ] Vídeo HLS: latência <3s
- [ ] Vídeo WebRTC: latência <500ms
- [ ] Ingestão: >1000 detecções/s
- [ ] Frontend: Lighthouse >90

### Escala
- [ ] 250 câmeras simultâneas estáveis
- [ ] 100 usuários concorrentes
- [ ] 50 streams simultâneos por usuário
- [ ] AI Service processando 250 FPS (1 frame/s por câmera)
- [ ] AWS Auto Scaling funcionando (2-10 instâncias)

### Recursos
- [ ] CPU <70% (carga normal)
- [ ] RAM <80% (carga normal)
- [ ] GPU <80% (AI Service GPU mode)
- [ ] Disco <85%
- [ ] Rede <80% capacidade
- [ ] **AWS:** Custo dentro do orçamento

### Alta Disponibilidade
- [ ] AI Service com 2+ réplicas (GPU ou EC2)
- [ ] **Modo Híbrido:** Fallback GPU → AWS funcionando
- [ ] **Circuit Breaker:** Testado e funcionando
- [ ] Kong com health checks
- [ ] PostgreSQL com réplica de leitura
- [ ] Redis Cluster configurado
- [ ] Failover automático funcionando

### Observabilidade
- [ ] Prometheus coletando métricas (incluindo AWS)
- [ ] Grafana com dashboards
- [ ] Loki agregando logs
- [ ] Jaeger com tracing
- [ ] Alertas configurados (Slack + PagerDuty)
- [ ] **AWS:** CloudWatch Alarms configurados
- [ ] **AWS:** Billing Alerts configurados

### Segurança
- [ ] HTTPS em produção (Kong SSL termination)
- [ ] JWT via Keycloak
- [ ] Rate limiting ativo (Kong)
- [ ] Senhas criptografadas
- [ ] WAF configurado (CloudFlare)
- [ ] **AWS:** IAM Roles com least privilege
- [ ] **AWS:** VPC Endpoints para Rekognition

---

## 🔧 CONFIGURAÇÕES PARA AJUSTE FINO

### HAProxy
```
# CONFIGURÁVEL: Timeouts
timeout connect 5s
timeout client 30s
timeout server 30s
timeout tunnel 1h    # Para WebRTC/WebSocket
```

### Kong
```yaml
# CONFIGURÁVEL: Rate Limiting
plugins:
  - name: rate-limiting
    config:
      minute: 100
      hour: 1000
      policy: redis
      redis_host: redis
```

### AI Service
```python
# CONFIGURÁVEL: Performance (comum)
CONFIDENCE_THRESHOLD = 0.5   # Threshold de detecção (0.0-1.0)
BATCH_SIZE = 8               # Frames por batch

# GPU Mode
GPU_DEVICE = "cuda:0"        # Qual GPU usar
GPU_MEMORY_FRACTION = 0.8    # % da GPU a usar
WORKERS_PER_GPU = 2          # Workers por GPU
YOLO_MODEL = "yolov8s.pt"    # n=nano, s=small, m=medium, l=large

# AWS Mode
AWS_REGION = "us-east-1"     # Região (us-east-1 é mais barato)
AWS_MAX_CONCURRENT = 50      # Requests simultâneas ao Rekognition
AWS_RETRY_ATTEMPTS = 3       # Tentativas em caso de erro

# Hybrid Mode
FALLBACK_TIMEOUT = 5.0       # Timeout para fallback (segundos)
CIRCUIT_BREAKER_THRESHOLD = 5 # Falhas para abrir circuit
CIRCUIT_BREAKER_RESET = 60   # Segundos para fechar circuit
```

### AWS Auto Scaling
```hcl
# CONFIGURÁVEL: Scaling
min_workers = 2              # Mínimo de instâncias
max_workers = 10             # Máximo de instâncias
scale_up_threshold = 70      # CPU % para scale up
scale_down_threshold = 30    # CPU % para scale down
cooldown_period = 300        # Segundos entre scaling
instance_type = "c5.xlarge"  # 4 vCPU, 8GB RAM
```

### MediaMTX
```yaml
# CONFIGURÁVEL: Performance vs Latência
hlsSegmentDuration: 2s    # 1s=baixa latência, 4s=menos CPU
writeQueueSize: 1024      # Aumentar se drops de frames
```

### PostgreSQL
```sql
-- CONFIGURÁVEL: Tuning para 250 câmeras
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 16MB
maintenance_work_mem = 512MB
max_connections = 200
```

### Redis
```
# CONFIGURÁVEL: Memória
maxmemory 1gb
maxmemory-policy allkeys-lru
```

---

## 📅 CRONOGRAMA ATUALIZADO

| Semana | Fase | Entregas |
|--------|------|----------|
| 1 | Infra Core | ~~HAProxy~~✅, ~~MediaMTX~~✅, ~~Nginx~~✅, ~~Kong~~✅, Keycloak |
| 2 | Backend + IA | **AI Service (FastAPI + YOLO + TF)**, PgBouncer, MinIO |
| 3 | Frontend | Bundle otimizado, Player leve, Virtual scroll |
| 4 | Observabilidade | Prometheus, Grafana, Loki, Jaeger, Alertmanager |

**Data de entrega:** Final de Janeiro 2025

---

## 📝 SESSÃO 16/12/2024 - Correções e Melhorias

### ✅ Problemas Corrigidos

#### 1. Django Admin sem CSS
**Problema:** Admin Django aparecia sem formatação (HTML puro).

**Causa:** Arquivos estáticos não estavam sendo servidos corretamente através do Kong/HAProxy.

**Solução:**
- Adicionada rota `/static` e `/media` no Kong (`kong/kong.yml`)
- Kong agora roteia arquivos estáticos para Nginx
- Configurado `CSRF_TRUSTED_ORIGINS` no Django para aceitar requests via proxy
- Criados scripts de correção: `fix-css.bat`, `check-static.bat`

**Arquivos modificados:**
- `kong/kong.yml` - Nova rota `django-static`
- `backend/config/settings.py` - CSRF origins + cookies config
- `fix-css.bat` - Script automático de correção
- `check-static.bat` - Script de diagnóstico
- `TROUBLESHOOTING-CSS.md` - Guia completo
- `README-CSS-FIX.md` - Guia rápido

#### 2. Erro CSRF 403 no Django Admin
**Problema:** Login no admin retornava erro "Verificação CSRF falhou".

**Causa:** Django bloqueando requests vindos através de Kong/HAProxy.

**Solução:**
```python
# settings.py
CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    # ... outras origens
]

CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

if DEBUG:
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
```

#### 3. Erro 503 no HAProxy
**Problema:** HAProxy retornando 503 ao acessar `/admin/`.

**Causa:** HAProxy roteando para Kong, mas Kong não tinha rota configurada.

**Solução:**
- Verificado que Kong já tinha rota `/admin` configurada
- Problema era que backend estava reiniciando (healthcheck)
- Aguardar backend ficar "healthy" antes de acessar

### 📁 Arquivos Criados

1. **fix-css.bat** - Script automático de correção de CSS
2. **check-static.bat** - Script de diagnóstico de arquivos estáticos
3. **open-admin.bat** - Script para abrir admin pela porta correta
4. **diagnose.bat** - Script de diagnóstico completo do sistema
5. **TROUBLESHOOTING-CSS.md** - Guia completo de troubleshooting
6. **README-CSS-FIX.md** - Guia rápido de uso dos scripts

### 🔧 Configurações Validadas

#### Arquitetura de Fluxo Confirmada
```
Fluxo de Usuário (React App / API):
Cloudflare (WAF/DDoS/SSL) → HAProxy → Kong → Backend Django

Fluxo de Vídeo (Playback):
Cloudflare (Cache HLS) → HAProxy → MediaMTX

Fluxo de Câmera (Ingestão):
Câmera (RTSP) → HAProxy (TCP Balance) → MediaMTX

Fluxo de Arquivos Estáticos:
Cloudflare → HAProxy → Kong → Nginx
```

#### HAProxy Configurado
- ✅ Roteamento de `/admin/` para Kong
- ✅ Roteamento de `/api/` para Kong
- ✅ Roteamento de `/static/` para Kong → Nginx
- ✅ Roteamento de vídeo direto para MediaMTX (bypass Kong)
- ✅ Sticky sessions para WebRTC
- ✅ Health checks funcionando

#### Kong Configurado
- ✅ Rota `/api` → Backend Django
- ✅ Rota `/admin` → Backend Django
- ✅ Rota `/static` → Nginx (NOVO)
- ✅ Rota `/media` → Nginx (NOVO)
- ✅ Rota `/fast-api` → Gateway FastAPI
- ✅ Rate limiting configurado
- ✅ CORS configurado
- ✅ Prometheus metrics habilitadas

### 🎯 Próximas Ações

1. **Testar fluxo completo:**
   - [ ] Login no admin funcionando
   - [ ] CSS carregando corretamente
   - [ ] API acessível via Kong
   - [ ] Arquivos estáticos servidos

2. **Commit das mudanças:**
   ```bash
   git add .
   git commit -m "fix: corrige CSS do Django Admin e CSRF via Kong/HAProxy
   
   - Adiciona rota de static files no Kong
   - Configura CSRF_TRUSTED_ORIGINS para proxies
   - Cria scripts de diagnóstico e correção
   - Adiciona documentação de troubleshooting"
   ```

3. **Continuar com Fase 1.5:** Implementar Keycloak

### 📊 Status Atual

**Infraestrutura Core (Fase 1):**
- [x] HAProxy (Load Balancer)
- [x] MediaMTX (Streaming)
- [x] Nginx (Arquivos Estáticos)
- [x] Kong (API Gateway)
- [x] Django Admin acessível e funcional
- [ ] Keycloak (Auth/Identity) ← PRÓXIMO

**Validações Pendentes:**
- [ ] Teste de carga com 50 câmeras
- [ ] Teste de failover do backend
- [ ] Teste de rate limiting do Kong
- [ ] Monitoramento com Prometheus

---

## 🚨 RISCOS E MITIGAÇÕES

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| GPU não disponível | Crítico | Fallback para AWS Rekognition (modo híbrido) |
| AI Service sobrecarregado | Alto | Auto-scaling (EC2), rate limiting, batch processing |
| **Custo AWS explode** | **Alto** | Monitorar billing, alertas de custo, reduzir FPS, detecção de movimento |
| **Latência AWS alta** | Médio | VPC Endpoints, região mais próxima, cache de resultados |
| **AWS throttling** | Médio | Exponential backoff, aumentar service quotas |
| MediaMTX não aguenta 250 câmeras | Alto | Testar com 50, 100, 150 incrementalmente |
| Disco enche rápido (8TB/semana) | Alto | MinIO lifecycle, limpeza automática, alertas |
| Latência de rede alta | Médio | CDN para vídeo, compressão |
| PostgreSQL lento | Alto | PgBouncer, índices, réplicas de leitura |
| Frontend pesado | Médio | Code splitting, lazy loading |

---

## 🎯 PRÓXIMOS PASSOS

1. **Implementar Kong API Gateway** (Fase 1.4)
2. **Criar AI Service com FastAPI** (Fase 2.1) ← PRIORIDADE ALTA
   - Começar com GPU Provider (desenvolvimento local)
   - Adicionar AWS Provider
   - Implementar Hybrid Provider
3. **Configurar Keycloak** (Fase 1.5)
4. **Implementar MinIO** (Fase 2.4)
5. **Configurar stack de observabilidade** (Fase 4.1)
6. **Deploy AWS** (após validação local)
   - Criar infraestrutura Terraform
   - Configurar Auto Scaling
   - Testar failover híbrido