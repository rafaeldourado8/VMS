# 📚 Índice Completo da Documentação VMS

Toda a documentação do sistema organizada por categoria.

---

## 🚀 Quick Start

- **[README Principal](../README.md)** - Visão geral do projeto
- **[Roadmap de Fases](./phases/README.md)** - Desenvolvimento por sprints
- **[System Overview](./SYSTEM_OVERVIEW.md)** - Arquitetura completa
- **[Tech Stack](./TECH_STACK.md)** - Tecnologias e justificativas

---

## 🤖 Sistema de Detecção de IA (NOVO)

### Principal
- **[Arquitetura Completa](./ai-detection/README.md)** - Sistema unificado de LPR
- **[Componentes](./ai-detection/components/README.md)** - Lista de todos os componentes

### Componentes Detalhados

#### Pipeline de Entrada
- [Frame Extractor](./ai-detection/components/FRAME_EXTRACTOR.md) - WebRTC (1-3 FPS)
- [Frame Buffer](./ai-detection/components/FRAME_BUFFER.md) - Queue assíncrona
- [Motion Detection](./ai-detection/components/MOTION_DETECTION.md) - Filtro de movimento

#### Detecção e Tracking
- [Vehicle Detection](./ai-detection/components/VEHICLE_DETECTION.md) - YOLO veículos
- [Multi-Object Tracker](./ai-detection/components/TRACKER.md) - Rastreamento
- [Track Buffer](./ai-detection/components/TRACK_BUFFER.md) - Buffer por veículo

#### Seleção de Qualidade
- [Quality Scorer](./ai-detection/components/QUALITY_SCORER.md) - Avaliação de frames
- [Best Frame Selection](./ai-detection/components/BEST_FRAME.md) - Seleção top 3

#### Reconhecimento
- [Plate Detection](./ai-detection/components/PLATE_DETECTION.md) - YOLO LPR
- [OCR Engine](./ai-detection/components/OCR_ENGINE.md) - Fast-Plate-OCR

#### Validação e Envio
- [Consensus Engine](./ai-detection/components/CONSENSUS_ENGINE.md) - Votação
- [Dedup Cache](./ai-detection/components/DEDUP_CACHE.md) - Redis cache
- [Event Producer](./ai-detection/components/EVENT_PRODUCER.md) - RabbitMQ

---

## 🎥 Streaming

- **[Streaming Overview](./streaming/STREAMING.md)** - MediaMTX + HLS + Thumbnails
- **[Thumbnail Optimization](./streaming/THUMBNAIL_OPTIMIZATION.md)** - Cache após 10s

---

## 🔍 Detecção (Legacy)

- **[LPR Detection](./detection/LPR.md)** - Sistema atual (YOLO + OCR)

---

## ⚡ Performance

- **[Performance Overview](./performance/PERFORMANCE.md)** - Todas as otimizações
- **[Paginação](./performance/PAGINATION.md)** - 10 câmeras por página
- **[Lazy Loading](./performance/LAZY_LOADING.md)** - Intersection Observer
- **[Screenshot Cache](./performance/SCREENSHOT_CACHE.md)** - 10s → imagem estática

---

## 💰 Cost Optimization

- **[Cost Overview](./cost-optimization/COST_OPTIMIZATION.md)** - Economia de $531k/mês
- **[Bandwidth](./cost-optimization/BANDWIDTH.md)** - $5k vs $520k
- **[CPU](./cost-optimization/CPU.md)** - $500 vs $10k (CPU-only)
- **[Storage](./cost-optimization/STORAGE.md)** - $250 vs $6k

---

## 📋 Roadmap

### Por Fase
- **[Fase 0: Base](./phases/phase-0/)** - Streaming + Backend + Frontend ✅
- **[Fase 1: Dashboard](./phases/phase-1/)** - Detecções em tempo real
- **[Fase 2: Blacklist](./phases/phase-2/)** - Sistema de alertas
- **[Fase 3: Recording](./phases/phase-3/)** - Gravação + Playback 🔄
- **[Fase 4: Sentinela](./phases/phase-4/)** - Busca retroativa
- **[Fase 5: Multi-Tenant](./phases/phase-5/)** - 1 DB por cidade
- **[Fase 6: Analytics](./phases/phase-6/)** - Relatórios

### Por Sprint
- **[Sprint 1](./sprints/sprint-1/)** - Streaming básico ✅
- **[Sprint 2](./sprints/sprint-2/)** - LPR Detection ✅
- **[Sprint 3](./sprints/sprint-3/)** - Recording & Playback 🔄

---

## 📊 Diagramas

### Arquitetura
- [Sistema Completo](./system-architecture.excalidraw.json)
- [Streaming](./streaming/streaming-architecture.excalidraw.json)
- [Thumbnail Optimization](./streaming/thumbnail-optimization.excalidraw.json)

### Performance
- [Otimizações](./performance/performance-optimizations.excalidraw.json)
- [Cost Savings](./cost-optimization/cost-savings.excalidraw.json)

### Detecção
- [LPR Pipeline](./detection/lpr-pipeline.excalidraw.json)
- [AI Detection Pipeline](./ai-detection/ai-pipeline.excalidraw.json) (TODO)

---

## 🛠️ Desenvolvimento

- **[Regras de Desenvolvimento](../.amazonq/prompts/development-rules.md)** - Workflow obrigatório
- **[Template de Task](./TASK_TEMPLATE.md)** - Documentação estruturada
- **[Functions List](./FUNCTIONS_LIST.md)** - Todas as funções do sistema

---

## 📐 Planejamento

- **[Capacity Planning](./CAPACITY_PLANNING_FORMULAS.md)** - Fórmulas de dimensionamento
- **[Roadmap Simple](./ROADMAP_SIMPLE.md)** - Visão simplificada
- **[Roadmap V2 30 Days](./ROADMAP_V2_30_DAYS.md)** - Plano de 30 dias

---

## 🔗 Links Externos

### Tecnologias
- [MediaMTX](https://github.com/bluenviron/mediamtx)
- [YOLOv8](https://docs.ultralytics.com/)
- [Fast-Plate-OCR](https://github.com/ankandrew/fast-plate-ocr)
- [Django](https://docs.djangoproject.com/)
- [React](https://react.dev/)
- [HLS.js](https://github.com/video-dev/hls.js/)

### AWS
- [Pricing Calculator](https://calculator.aws)
- [Data Privacy FAQ](https://aws.amazon.com/compliance/data-privacy-faq/)

---

## 📝 Estrutura de Documentação

### Por Task (Template)
```
docs/phases/[FASE]/[TASK_NAME]/
├── WHAT.md           # O que foi feito
├── WHY.md            # Por que (alternativas, trade-offs)
├── IMPACT.md         # Impacto (benefícios, métricas)
├── METRICS.md        # Cálculos (DAU, RPS, custos)
├── IMPORTANCE.md     # Quando usar/não usar
└── diagram.excalidraw.json  # Diagrama visual
```

### Por Componente (AI Detection)
```
docs/ai-detection/components/[COMPONENT]/
├── README.md         # Documentação completa
├── examples/         # Exemplos de uso
├── tests/            # Casos de teste
└── diagram.excalidraw.json  # Diagrama
```

---

## 🔍 Busca Rápida

### Por Funcionalidade
- **Streaming**: [STREAMING.md](./streaming/STREAMING.md)
- **Detecção**: [ai-detection/README.md](./ai-detection/README.md)
- **Gravação**: [phases/phase-3/](./phases/phase-3/)
- **Busca**: [phases/phase-4/](./phases/phase-4/)
- **Analytics**: [phases/phase-6/](./phases/phase-6/)

### Por Tecnologia
- **MediaMTX**: [STREAMING.md](./streaming/STREAMING.md)
- **YOLO**: [ai-detection/components/](./ai-detection/components/)
- **OCR**: [OCR_ENGINE.md](./ai-detection/components/OCR_ENGINE.md)
- **Redis**: [DEDUP_CACHE.md](./ai-detection/components/DEDUP_CACHE.md)
- **RabbitMQ**: [EVENT_PRODUCER.md](./ai-detection/components/EVENT_PRODUCER.md)

### Por Otimização
- **CPU**: [CPU.md](./cost-optimization/CPU.md)
- **Banda**: [BANDWIDTH.md](./cost-optimization/BANDWIDTH.md)
- **Storage**: [STORAGE.md](./cost-optimization/STORAGE.md)
- **Performance**: [PERFORMANCE.md](./performance/PERFORMANCE.md)

---

## 📈 Status do Projeto

### ✅ Implementado
- Streaming (MediaMTX + HLS)
- Backend API (Django + PostgreSQL + Redis + RabbitMQ)
- Frontend (React + Vite + TypeScript + TailwindCSS)
- LPR Detection básico (YOLO + OCR)
- Paginação (10 câmeras/página)
- Lazy Loading
- Screenshot Cache
- Monitoring (Prometheus)

### 🔄 Em Andamento
- **AI Detection Pipeline** (Sistema unificado)
- Recording & Playback
- Multi-Tenant + Planos

### 📋 Planejado
- Dashboard de Detecções
- Sistema de Blacklist
- Sentinela (Busca Retroativa)
- Analytics & Relatórios

---

## 🎯 Próximos Passos

1. **Implementar AI Detection Pipeline** (2-3 semanas)
   - Setup base + componentes core
   - Pipeline completo
   - Integração com Backend
   - Testes e otimização

2. **Recording & Playback** (1-2 semanas)
   - Recording Service
   - Playback API
   - Timeline Component

3. **Multi-Tenant** (1 semana)
   - 1 DB por cidade
   - Planos (Basic/Pro/Premium)
   - Usuários transferíveis

---

## 📞 Suporte

Para dúvidas sobre a documentação:
1. Verificar [INDEX.md](./INDEX.md) (este arquivo)
2. Buscar na seção específica
3. Verificar diagramas Excalidraw
4. Consultar código-fonte com comentários
