# Sprint 1: FastAPI Service Base

## Objetivo
Criar a estrutura base do FastAPI service para timeline

## Checklist

### 📁 Estrutura de Arquivos
- [x] Criar `services/timeline/`
- [x] Criar `services/timeline/Dockerfile`
- [x] Criar `services/timeline/main.py`
- [x] Criar `services/timeline/requirements.txt`
- [x] Criar `services/timeline/models.py`
- [x] Criar `services/timeline/config.py`

### 🐳 Docker Setup
- [x] Dockerfile baseado em python:3.11-slim
- [x] Instalar ffmpeg para análise de vídeo
- [x] Expor porta 8007
- [x] Configurar uvicorn

### 📦 Dependências
- [x] fastapi
- [x] uvicorn[standard]
- [x] pydantic
- [x] aiofiles
- [x] httpx
- [x] python-multipart
- [x] prometheus-client (adicionado)

### 🔧 Configuração Base
- [x] Variáveis de ambiente
  - [x] `RECORDINGS_PATH` (padrão: /recordings)
  - [x] `CACHE_TTL` (padrão: 300)
  - [x] `MAX_SCAN_DEPTH` (padrão: 3)
- [x] CORS middleware
- [x] Logging configurado (JSON estruturado)

### 📊 Models Pydantic
- [x] `TimelineBlock` - Bloco de gravação
- [x] `CameraTimeline` - Timeline de uma câmera
- [x] `VideoSegment` - Segmento de vídeo
- [x] `IndexStatus` - Status da indexação

### 🛣 Endpoints Base
- [x] `GET /health` - Health check
- [x] `GET /status` - Status do serviço
- [x] `GET /cameras` - Lista câmeras disponíveis
- [x] `POST /scan` - Força scan completo
- [x] `GET /metrics` - Métricas Prometheus (adicionado)

### ✅ Testes
- [x] Health check funciona
- [x] Serviço inicia sem erros
- [x] CORS configurado corretamente
- [x] Logs aparecem corretamente (JSON estruturado)
- [x] Métricas Prometheus funcionando

## Critérios de Aceite
- [x] Serviço FastAPI roda na porta 8007
- [x] Health check retorna 200
- [x] Dockerfile build sem erros
- [x] Logs estruturados funcionando
- [x] Métricas /metrics disponíveis

## Estimativa: 4 horas