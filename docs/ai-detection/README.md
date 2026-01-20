# 🤖 Sistema de Detecção de IA - Arquitetura Completa

Sistema inteligente de detecção de placas veiculares (LPR) com pipeline otimizado para alta precisão e baixo custo.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Componentes](#componentes)
- [Pipeline de Processamento](#pipeline-de-processamento)
- [Análise dos Sistemas Existentes](#análise-dos-sistemas-existentes)
- [Decisões Técnicas](#decisões-técnicas)
- [Implementação](#implementação)

---

## 🎯 Visão Geral

### Objetivo
Detectar e reconhecer placas veiculares em tempo real com:
- **Alta precisão**: Consenso de múltiplas leituras (≥60%)
- **Baixa latência**: WebRTC para IA (vs HLS para usuários)
- **Baixo custo**: CPU-only, motion detection, frame skipping
- **Zero duplicatas**: Cache Redis com TTL de 5 minutos

### Fluxo Simplificado
```
Camera RTSP → MediaMTX → WebRTC (IA) → Pipeline → Backend
                       └→ HLS (Usuários)
```

### Métricas Alvo
- **Latência**: <500ms (WebRTC vs 10-30s HLS)
- **Precisão**: >95% (consenso multi-round)
- **FPS**: 1-3 FPS (vs 30 FPS original = 90% economia)
- **CPU**: <30% por câmera (motion detection + frame skipping)

---

## 🏗️ Arquitetura

### Fluxo Detalhado

```
Camera RTSP
   ↓
MediaMTX
   ├─ WebRTC (IA – low latency, FPS controlado)
   └─ HLS (Usuários) (já funciona, nunca mexer)
   ↓
Frame Extractor (1-3 FPS)
   ↓
Frame Buffer (Queue Assíncrona)
   ↓
Motion Detection? ──NO──> Drop Frame (70-80%)
   ↓ YES
Vehicle Detection? ──NO──> Drop Frame
   ↓ YES
Multi-Object Tracking (ByteTrack)
   ↓
Track Buffer (10-30 frames por veículo)
   ↓
Frame Quality Scoring (Blur/Angle/Contrast/Size)
   ↓
Best Frame Selection (Top 3)
   ↓
Plate Detection (YOLO LPR)
   ↓
OCR (Fast-Plate-OCR)
   ↓
Consensus Engine (3-5 leituras, ≥60%)
   ↓
Duplicado? ──YES──> Drop Event
   ↓ NO
Dedup Cache (Redis TTL 5min)
   ↓
Event Producer (RabbitMQ)
   ↓
Backend API Consumer
```

### Estrutura de Diretórios

```
services/ai_detection/
├── core/                       # Componentes principais
│   ├── motion_detector.py      # Detecção de movimento
│   ├── vehicle_detector.py     # Detecção de veículos
│   ├── plate_detector.py       # Detecção de placas
│   ├── ocr_engine.py           # Reconhecimento OCR
│   ├── tracker.py              # Rastreamento multi-objeto
│   └── quality_scorer.py       # Avaliação de qualidade
│
├── pipeline/                   # Pipeline de processamento
│   ├── frame_extractor.py      # Extração de frames WebRTC
│   ├── frame_buffer.py         # Buffer assíncrono
│   ├── consensus_engine.py     # Motor de consenso
│   └── dedup_cache.py          # Cache de deduplicação
│
├── integration/                # Integrações externas
│   ├── mediamtx_client.py      # Cliente WebRTC
│   ├── api_client.py           # Cliente Backend API
│   └── rabbitmq_producer.py    # Produtor de eventos
│
├── api/                        # API de controle
│   └── control_api.py          # Flask API
│
├── config/                     # Configurações
│   └── settings.py             # Variáveis de ambiente
│
├── main.py                     # Entry point
├── Dockerfile                  # Container otimizado
└── requirements.txt            # Dependências
```

---

## 🔧 Componentes

### [1. Frame Extractor](./components/FRAME_EXTRACTOR.md)
**Função**: Extrai frames do stream WebRTC do MediaMTX

**Input**: WebRTC stream (baixa latência)  
**Output**: Frames RGB (1-3 FPS)

**Características**:
- FPS throttle configurável (1-3 FPS)
- Economia de 90% de processamento vs 30 FPS
- Reconexão automática em caso de falha

---

### [2. Frame Buffer](./components/FRAME_BUFFER.md)
**Função**: Queue assíncrona para desacoplar captura de processamento

**Input**: Frames do extractor  
**Output**: Frames para motion detection

**Características**:
- Queue thread-safe (asyncio)
- Tamanho máximo configurável
- Drop de frames antigos se buffer cheio

---

### [3. Motion Detection](./components/MOTION_DETECTION.md)
**Função**: Filtra frames sem movimento (economia de CPU)

**Input**: Frames do buffer  
**Output**: Frames com movimento detectado

**Características**:
- OpenCV MOG2 (Background Subtraction)
- Economia de 70-80% de processamento
- Sensibilidade configurável

**Algoritmo**:
```python
# Detecta mudanças entre frames
# Se mudança < threshold → Drop frame
# Se mudança ≥ threshold → Processa
```

---

### [4. Vehicle Detection](./components/VEHICLE_DETECTION.md)
**Função**: Detecta veículos no frame usando YOLO

**Input**: Frames com movimento  
**Output**: Bounding boxes de veículos

**Características**:
- YOLOv8n (nano - rápido)
- Classes: car, truck, motorcycle, bus
- Confidence threshold: >0.5

**Otimizações**:
- Processa 1 a cada 3 frames (frame skipping)
- CPU-only (PyTorch)
- Modelo compacto (6MB)

---

### [5. Multi-Object Tracker](./components/TRACKER.md)
**Função**: Rastreia veículos entre frames para acumular leituras

**Input**: Detecções de veículos  
**Output**: Tracks completos (veículo saiu do FOV)

**Características**:
- ByteTrack ou DeepSORT
- IoU-based matching (threshold: 0.3)
- Timeout: 5 segundos sem detecção

**Por que é importante**:
- Acumula 10-30 frames por veículo
- Permite consenso de múltiplas leituras
- Reduz falsos positivos

---

### [6. Track Buffer](./components/TRACK_BUFFER.md)
**Função**: Armazena frames de cada veículo rastreado

**Input**: Frames do track ativo  
**Output**: Conjunto de frames quando veículo sai do FOV

**Características**:
- 10-30 frames por veículo
- Armazena frame + metadata (timestamp, bbox)
- Libera memória após processamento

---

### [7. Quality Scorer](./components/QUALITY_SCORER.md)
**Função**: Avalia qualidade de cada frame para escolher o melhor

**Input**: Frames do track buffer  
**Output**: Score de qualidade (0-100)

**Métricas**:

1. **Blur Detection** (Laplacian Variance)
   - Frame nítido: score alto
   - Frame borrado: score baixo

2. **Ângulo da Placa** (Perspectiva)
   - Placa frontal: score alto
   - Placa lateral: score baixo

3. **Contraste** (Histograma)
   - Alto contraste: score alto
   - Baixo contraste: score baixo

4. **Tamanho da Placa** (Pixels)
   - Placa grande: score alto
   - Placa pequena: score baixo

**Fórmula**:
```
Score = (blur × 0.3) + (angle × 0.3) + (contrast × 0.2) + (size × 0.2)
```

---

### [8. Best Frame Selection](./components/BEST_FRAME.md)
**Função**: Seleciona o melhor frame do track para OCR

**Input**: Frames + scores  
**Output**: Frame com maior score

**Estratégia**:
- Ordena frames por score
- Seleciona top 3
- Usa todos para consenso

---

### [9. Plate Detection](./components/PLATE_DETECTION.md)
**Função**: Detecta placa no frame do veículo

**Input**: Frame do veículo  
**Output**: Bounding box da placa

**Características**:
- YOLO fine-tuned para placas
- Modelos disponíveis: yolov8n/s/m/l/x
- Confidence threshold: >0.6

**Pré-processamento**:
- Crop da região do veículo
- Resize para tamanho padrão
- Conversão para escala de cinza

---

### [10. OCR Engine](./components/OCR_ENGINE.md)
**Função**: Reconhece texto da placa

**Input**: Imagem da placa  
**Output**: Texto da placa + confidence

**Características**:
- Fast-Plate-OCR (ONNX runtime)
- Suporte multi-país (Brasil, Argentina, etc)
- CPU-optimized

**Alternativas avaliadas**:
- ❌ Tesseract: Lento, menos preciso
- ❌ PaddleOCR: Complexo, GPU-dependent
- ✅ Fast-Plate-OCR: Rápido, preciso, CPU-only

---

### [11. Consensus Engine](./components/CONSENSUS_ENGINE.md)
**Função**: Determina placa correta por votação

**Input**: 3-5 leituras de OCR  
**Output**: Placa validada + confidence

**Estratégias**:

1. **Simple Majority** (Maioria Simples)
   - Se placa aparece >50% → Vence
   - Exemplo: [ABC1234, ABC1234, ABC1234, XYZ5678] → ABC1234

2. **Similarity Voting** (Similaridade)
   - Agrupa placas similares (>80%)
   - Exemplo: [ABC1234, ABC1Z34, ABC1234] → ABC1234
   - Usa difflib.SequenceMatcher

3. **Highest Confidence** (Fallback)
   - Se sem consenso → Maior confidence
   - Exemplo: [ABC1234(0.9), XYZ5678(0.7)] → ABC1234

**Requisitos**:
- Mínimo 3 leituras
- Consenso ≥60%
- Confidence mínima: 0.75

---

### [12. Deduplication Cache](./components/DEDUP_CACHE.md)
**Função**: Evita enviar mesma placa múltiplas vezes

**Input**: Placa validada  
**Output**: Placa única (se não duplicada)

**Características**:
- Redis com TTL de 5 minutos
- Key: `plate:{camera_id}:{plate_text}`
- Similaridade: 80% (SequenceMatcher)

**Exemplo**:
```
10:00 → ABC1234 (enviado)
10:02 → ABC1234 (bloqueado - duplicata)
10:06 → ABC1234 (enviado - TTL expirou)
```

---

### [13. Event Producer](./components/EVENT_PRODUCER.md)
**Função**: Envia eventos para o Backend via RabbitMQ

**Input**: Detecção validada  
**Output**: Mensagem na fila

**Payload**:
```json
{
  "plate": "ABC1234",
  "confidence": 0.92,
  "method": "simple_majority",
  "camera_id": 1,
  "timestamp": "2024-01-15T10:30:00Z",
  "image_path": "/captures/abc1234_123456.jpg",
  "metadata": {
    "track_id": 42,
    "frames_analyzed": 15,
    "best_frame_score": 87.5
  }
}
```

---

## 🔄 Pipeline de Processamento

### Taxas de Drop (Otimização)

| Etapa | Drop Rate | Frames Restantes |
|-------|-----------|------------------|
| Input (30 FPS) | - | 30 FPS |
| Frame Extractor | 90% | 3 FPS |
| Motion Detection | 70% | 0.9 FPS |
| Vehicle Detection | 50% | 0.45 FPS |
| **Total** | **98.5%** | **0.45 FPS** |

**Resultado**: Processa apenas 1.5% dos frames originais!

---

## 📊 Análise dos Sistemas Existentes

### Sistema 1: `lpr_detection` (Atual)

**Localização**: `services/lpr_detection/`

#### ✅ Pontos Fortes

1. **Tracking de Veículos** (`tracking.py`)
   - IoU-based matching
   - Timeout configurável (5s)
   - Acumula detecções por veículo

2. **Sistema de Votação** (`voting.py`)
   - 3 estratégias (majority, similarity, confidence)
   - Consenso configurável
   - Classificação de confiança

3. **Fast-Plate-OCR** (`detection.py`)
   - ONNX runtime (rápido)
   - CPU-optimized
   - Suporte multi-país

4. **Integração Backend** (`main.py`, `api_client.py`)
   - API REST para controle
   - RabbitMQ para eventos
   - PostgreSQL para persistência

5. **Docker Otimizado** (`Dockerfile.optimized`)
   - Multi-stage build
   - CPU-only PyTorch
   - Health checks

#### ❌ Pontos Fracos

1. **Sem Motion Detection**
   - Processa todos os frames
   - Desperdício de CPU

2. **Sem Quality Scoring**
   - Não escolhe melhor frame
   - Pode usar frames ruins

3. **Sem Deduplicação**
   - Pode enviar duplicatas
   - Sem cache Redis

4. **RTSP Direto**
   - Alta latência
   - Sem WebRTC

5. **Pipeline Simples**
   - Sem buffer assíncrono
   - Sem validação multi-round

---

### Sistema 2: `alpr-yolov8-python-ocr` (Clonado)

**Localização**: `services/alpr-yolov8-python-ocr/`

#### ✅ Pontos Fortes

1. **Motion Detection** (`server.py`)
   - OpenCV MOG2
   - Background subtraction
   - Economia de 70-80% CPU

2. **Quality Scoring** (`utils.py`)
   - Blur detection (Laplacian)
   - Pré-processamento avançado
   - Contour detection

3. **Validação Multi-Round** (`server.py`)
   - 3-5 leituras por veículo
   - Consenso ≥60%
   - Filtro de resultados

4. **Deduplicação Temporal** (`server.py`)
   - Cache in-memory (5min)
   - Similaridade 80%
   - Evita duplicatas

5. **WebSocket Server** (`server.py`)
   - Tempo real
   - Múltiplos clientes
   - Reconexão automática

6. **Pré-processamento Avançado** (`utils.py`)
   - Gaussian blur
   - Threshold adaptativo
   - Morphological operations
   - Contour extraction

#### ❌ Pontos Fracos

1. **Sem Tracking de Veículos**
   - Não rastreia entre frames
   - Perde contexto

2. **Sem Integração VMS**
   - Não usa Backend API
   - Não usa RabbitMQ
   - MSSQL (não PostgreSQL)

3. **WebSocket (não ideal)**
   - Não é padrão do VMS
   - Complexidade extra

4. **Tesseract OCR**
   - Mais lento que Fast-Plate-OCR
   - Menos preciso
   - Multi-thread complexo

5. **Sem Controle de Câmeras**
   - Não tem API REST
   - Não integra com MediaMTX

---

## 🎯 Decisões Técnicas

### O que USAR de cada sistema

#### Do `lpr_detection`:
- ✅ **Tracking** (IoU-based) → Melhorar com ByteTrack
- ✅ **Voting System** → Manter e expandir
- ✅ **Fast-Plate-OCR** → Manter (melhor que Tesseract)
- ✅ **API Client + RabbitMQ** → Manter
- ✅ **Docker Otimizado** → Manter
- ✅ **Flask API** → Manter para controle

#### Do `alpr-yolov8-python-ocr`:
- ✅ **Motion Detection** (MOG2) → Adicionar
- ✅ **Quality Scoring** → Adicionar
- ✅ **Multi-round Validation** → Adicionar
- ✅ **Deduplication Cache** → Adicionar (migrar para Redis)
- ✅ **Pré-processamento Avançado** → Adicionar

### O que NÃO usar

#### Do `alpr-yolov8-python-ocr`:
- ❌ **WebSocket Server** → Usar RabbitMQ
- ❌ **Tesseract OCR** → Usar Fast-Plate-OCR
- ❌ **MSSQL** → Usar PostgreSQL do VMS
- ❌ **In-memory Cache** → Usar Redis

---

## 🚀 Implementação

### Fases de Desenvolvimento

#### **Fase 1: Setup Base** (2-3 dias)
- [ ] Criar estrutura `ai_detection/`
- [ ] Configurar Docker + requirements
- [ ] Setup Redis para cache
- [ ] Configurar variáveis de ambiente

#### **Fase 2: Core Components** (3-4 dias)
- [ ] `motion_detector.py` (OpenCV MOG2)
- [ ] `vehicle_detector.py` (YOLO)
- [ ] `plate_detector.py` (YOLO LPR)
- [ ] `ocr_engine.py` (Fast-Plate-OCR)
- [ ] `tracker.py` (ByteTrack)
- [ ] `quality_scorer.py` (Blur/Angle/Contrast)

#### **Fase 3: Pipeline** (3-4 dias)
- [ ] `frame_extractor.py` (WebRTC)
- [ ] `frame_buffer.py` (Async queue)
- [ ] `consensus_engine.py` (Voting)
- [ ] `dedup_cache.py` (Redis)

#### **Fase 4: Integration** (2-3 dias)
- [ ] `mediamtx_client.py` (WebRTC consumer)
- [ ] `api_client.py` (Backend API)
- [ ] `rabbitmq_producer.py` (Event queue)

#### **Fase 5: API & Control** (1-2 dias)
- [ ] `control_api.py` (Flask)
- [ ] Health checks
- [ ] Prometheus metrics

#### **Fase 6: Testing** (2-3 dias)
- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Benchmark de performance
- [ ] Ajuste de thresholds

#### **Fase 7: Documentation** (1-2 dias)
- [ ] Documentação de componentes
- [ ] Guia de configuração
- [ ] Troubleshooting
- [ ] Diagramas Excalidraw

---

## 📈 Métricas de Sucesso

### Performance
- **Latência**: <500ms (vs 10-30s HLS)
- **Throughput**: 10-20 câmeras por servidor
- **CPU**: <30% por câmera
- **Memória**: <500MB por câmera

### Qualidade
- **Precisão**: >95% (consenso)
- **Recall**: >90% (não perde veículos)
- **Falsos Positivos**: <5%
- **Duplicatas**: 0% (cache Redis)

### Custo
- **CPU**: $500/mês (vs $10k GPU)
- **Banda**: Mínima (WebRTC local)
- **Storage**: Mínimo (só best frames)

---

## 🔗 Links Relacionados

- [Componentes Detalhados](./components/)
- [Roadmap](../phases/README.md)
- [System Overview](../SYSTEM_OVERVIEW.md)
