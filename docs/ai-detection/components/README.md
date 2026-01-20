# Componentes do Sistema de Detecção de IA

Documentação detalhada de cada componente do pipeline de detecção.

---

## 📋 Lista de Componentes

### Pipeline de Entrada
1. **[Frame Extractor](./FRAME_EXTRACTOR.md)** - Extrai frames do WebRTC (1-3 FPS)
2. **[Frame Buffer](./FRAME_BUFFER.md)** - Queue assíncrona de frames
3. **[Motion Detection](./MOTION_DETECTION.md)** - Filtra frames sem movimento (70-80% drop)

### Detecção e Tracking
4. **[Vehicle Detection](./VEHICLE_DETECTION.md)** - Detecta veículos com YOLO
5. **[Multi-Object Tracker](./TRACKER.md)** - Rastreia veículos entre frames
6. **[Track Buffer](./TRACK_BUFFER.md)** - Armazena frames por veículo

### Seleção de Qualidade
7. **[Quality Scorer](./QUALITY_SCORER.md)** - Avalia qualidade dos frames
8. **[Best Frame Selection](./BEST_FRAME.md)** - Seleciona melhores frames

### Reconhecimento
9. **[Plate Detection](./PLATE_DETECTION.md)** - Detecta placas com YOLO LPR
10. **[OCR Engine](./OCR_ENGINE.md)** - Reconhece texto com Fast-Plate-OCR

### Validação e Envio
11. **[Consensus Engine](./CONSENSUS_ENGINE.md)** - Votação de múltiplas leituras
12. **[Dedup Cache](./DEDUP_CACHE.md)** - Evita duplicatas (Redis)
13. **[Event Producer](./EVENT_PRODUCER.md)** - Envia para Backend (RabbitMQ)

---

## 🔄 Fluxo Completo

```
Frame Extractor (1-3 FPS)
    ↓
Frame Buffer
    ↓
Motion Detection (drop 70-80%)
    ↓
Vehicle Detection
    ↓
Multi-Object Tracker
    ↓
Track Buffer (10-30 frames)
    ↓
Quality Scorer
    ↓
Best Frame Selection (top 3)
    ↓
Plate Detection
    ↓
OCR Engine (3-5 leituras)
    ↓
Consensus Engine (≥60%)
    ↓
Dedup Cache (5min TTL)
    ↓
Event Producer (RabbitMQ)
```

---

## 📊 Estatísticas de Drop

| Componente | Input | Drop | Output | Economia |
|------------|-------|------|--------|----------|
| Frame Extractor | 30 FPS | 90% | 3 FPS | 90% |
| Motion Detection | 3 FPS | 70% | 0.9 FPS | 70% |
| Vehicle Detection | 0.9 FPS | 50% | 0.45 FPS | 50% |
| **Total** | **30 FPS** | **98.5%** | **0.45 FPS** | **98.5%** |

---

## ⚡ Performance por Componente

| Componente | Tempo (ms) | CPU | Memória |
|------------|------------|-----|---------|
| Frame Extractor | 5 | 2% | 10MB |
| Motion Detection | 10 | 5% | 5MB |
| Vehicle Detection | 50 | 15% | 50MB |
| Tracker | 5 | 2% | 20MB |
| Quality Scorer | 15 | 5% | 10MB |
| Plate Detection | 30 | 10% | 30MB |
| OCR Engine | 100 | 20% | 100MB |
| Consensus | 5 | 1% | 5MB |
| Dedup Cache | 2 | 1% | 10MB |
| **Total** | **222ms** | **61%** | **240MB** |

**Por câmera**: ~250ms latência, ~60% CPU, ~250MB RAM

---

## 🎯 Componentes Críticos

### Alta Prioridade (Impacto Direto na Precisão)
1. **Quality Scorer** - Escolhe melhores frames
2. **Consensus Engine** - Valida leituras
3. **OCR Engine** - Reconhece placas

### Média Prioridade (Impacto na Performance)
4. **Motion Detection** - Economia de CPU
5. **Tracker** - Acumula leituras
6. **Dedup Cache** - Evita duplicatas

### Baixa Prioridade (Infraestrutura)
7. **Frame Extractor** - Captura básica
8. **Frame Buffer** - Queue simples
9. **Event Producer** - Envio assíncrono

---

## 🔧 Configuração Rápida

### Desenvolvimento (Precisão Máxima)
```bash
AI_FPS=5
MOTION_THRESHOLD=0.01
MIN_READINGS=7
CONSENSUS_THRESHOLD=0.7
MIN_CONFIDENCE=0.85
```

### Produção (Balanço)
```bash
AI_FPS=3
MOTION_THRESHOLD=0.03
MIN_READINGS=5
CONSENSUS_THRESHOLD=0.6
MIN_CONFIDENCE=0.75
```

### Alta Performance (Custo Mínimo)
```bash
AI_FPS=1
MOTION_THRESHOLD=0.05
MIN_READINGS=3
CONSENSUS_THRESHOLD=0.5
MIN_CONFIDENCE=0.70
```

---

## 📚 Documentação Relacionada

- [Visão Geral do Sistema](../README.md)
- [Análise dos Sistemas Existentes](../README.md#análise-dos-sistemas-existentes)
- [Decisões Técnicas](../README.md#decisões-técnicas)
- [Roadmap de Implementação](../README.md#implementação)
