# 📚 Documentação Técnica - VMS

> Sistema de Monitoramento de Vídeo com IA para detecção de placas veiculares

---

## 🚀 Quick Start

- **[Visão Geral do Sistema](./SYSTEM_OVERVIEW.md)** - Entenda o VMS em 5 minutos
- **[Stack Tecnológica](./TECH_STACK.md)** - Todas as tecnologias usadas
- **[Guia de Instalação](../README.md)** - Como rodar o projeto

---

## 📁 Documentação por Componente

### 🎥 [Streaming](./streaming/)
Sistema de distribuição de vídeo

- **[Arquitetura de Streaming](./streaming/STREAMING.md)**
  - MediaMTX configuration
  - HLS protocol
  - On-demand streams
  - Performance metrics

- **[Thumbnails Otimizados](./streaming/THUMBNAILS.md)**
  - Lazy loading strategy
  - Screenshot cache (10s)
  - Intersection Observer
  - Economia de 95% de banda

### 🤖 [Detection](./detection/)
Sistema de IA para detecção de placas

- **[LPR (License Plate Recognition)](./detection/LPR.md)**
  - YOLO + OCR pipeline
  - Frame skipping
  - ROI optimization
  - CPU-only strategy

### ⚡ [Performance](./performance/)
Otimizações de desempenho

- **[Performance Overview](./performance/PERFORMANCE.md)**
  - Frontend optimizations
  - Backend optimizations
  - Streaming optimizations
  - AI optimizations
  - Métricas e benchmarks

### 💰 [Cost Optimization](./cost-optimization/)
Estratégias de redução de custos

- **[Cost Optimization](./cost-optimization/COST_OPTIMIZATION.md)**
  - Economia de banda (95%)
  - CPU-only IA ($9,500/mês economizado)
  - Armazenamento eficiente (92%)
  - ROI de 31,811%

### 🔧 [Backend](./backend/)
API e serviços backend

- Django REST API
- Database models
- Services architecture
- Integration patterns

### 🎨 [Frontend](./frontend/)
Interface do usuário

- React components
- State management
- Caching strategy
- UI/UX patterns

### 🏗️ [Infrastructure](./infrastructure/)
DevOps e infraestrutura

- Docker setup
- Monitoring (Prometheus)
- Deployment
- Scaling strategies

---

## 📊 Documentos Principais

### [📋 Visão Geral do Sistema](./SYSTEM_OVERVIEW.md)
Entenda o VMS completo:
- O que é e o que resolve
- Funcionalidades principais
- Arquitetura geral
- Tipos de câmeras
- Fluxo de dados
- Casos de uso
- Diferenciais vs concorrentes

### [🛠️ Stack Tecnológica](./TECH_STACK.md)
Todas as tecnologias usadas:
- Backend (Django, PostgreSQL, Redis, RabbitMQ)
- Frontend (React, Vite, TypeScript, TailwindCSS)
- Streaming (MediaMTX, HLS.js, FFmpeg)
- IA/ML (YOLO, OCR, PyTorch)
- Infrastructure (Docker, Prometheus)
- Justificativas de escolha

### [⚡ Performance](./performance/PERFORMANCE.md)
Otimizações implementadas:
- Lazy loading (90% economia)
- Screenshot cache (95% economia)
- Frame skipping (66% economia)
- Database indexing (10-100x mais rápido)
- Métricas antes/depois

### [💰 Cost Optimization](./cost-optimization/COST_OPTIMIZATION.md)
Redução de custos:
- Banda: $515,000/mês economizado
- Computação: $9,500/mês economizado
- Armazenamento: $5,750/mês economizado
- Total: $531,850/mês economizado (99%)

---

## 🎯 Por Funcionalidade

### Streaming de Vídeo
1. [Arquitetura de Streaming](./streaming/STREAMING.md)
2. [Thumbnails Otimizados](./streaming/THUMBNAILS.md)
3. [Performance](./performance/PERFORMANCE.md#streaming-performance)

### Detecção de Placas
1. [LPR System](./detection/LPR.md)
2. [AI Optimization](./performance/PERFORMANCE.md#ia-performance)
3. [Cost Optimization](./cost-optimization/COST_OPTIMIZATION.md#computação-cpugpu)

### Gravação
1. [Recording Service](./streaming/STREAMING.md#gravação)
2. [Storage Optimization](./cost-optimization/COST_OPTIMIZATION.md#armazenamento)

### Busca Retroativa
1. [Sentinela Concept](./detection/LPR.md#sentinela-busca-retroativa)
2. [Implementation Guide](./backend/) (em desenvolvimento)

---

## 📈 Métricas e Benchmarks

### Performance
- **Frontend:** 1.2s first load, 60 FPS scroll
- **Backend:** <50ms API response, 500+ concurrent users
- **Streaming:** 2-4s latency, ilimitado concurrent
- **IA:** 30 FPS per camera, >90% accuracy

### Custos
- **Banda:** $5,000/mês (vs $520,000 sem otimização)
- **Computação:** $500/mês (vs $10,000 com GPU)
- **Storage:** $250/mês (vs $6,000 sem otimização)
- **Total:** $6,150/mês (vs $538,000)

### Escalabilidade
- ✅ 100 câmeras testadas
- ✅ 1000 usuários concurrent
- ✅ 10TB de gravações
- ⏳ 1000 câmeras (em teste)

---

## 🔍 Busca Rápida

### Por Problema
- **Site lento?** → [Performance](./performance/PERFORMANCE.md)
- **Custo alto?** → [Cost Optimization](./cost-optimization/COST_OPTIMIZATION.md)
- **Streaming travando?** → [Streaming](./streaming/STREAMING.md)
- **IA imprecisa?** → [LPR Detection](./detection/LPR.md)

### Por Tecnologia
- **Django** → [Tech Stack](./TECH_STACK.md#django-42)
- **React** → [Tech Stack](./TECH_STACK.md#react-18)
- **MediaMTX** → [Streaming](./streaming/STREAMING.md#mediamtx)
- **YOLO** → [LPR Detection](./detection/LPR.md#yolo)

### Por Feature
- **Thumbnails** → [Thumbnails](./streaming/THUMBNAILS.md)
- **Lazy Loading** → [Performance](./performance/PERFORMANCE.md#lazy-loading)
- **Cache** → [Performance](./performance/PERFORMANCE.md#cache)
- **ROI** → [LPR Detection](./detection/LPR.md#roi)

---

## 🛠️ Para Desenvolvedores

### Setup
```bash
# Clone
git clone <repo-url>
cd VMS

# Environment
cp .env.example .env

# Start
docker-compose up -d
```

### Estrutura
```
VMS/
├── backend/              # Django API
├── frontend/             # React App
├── services/
│   ├── lpr_detection/   # YOLO + OCR
│   ├── streaming/       # MediaMTX
│   └── recording/       # FFmpeg
├── docs/                # Esta documentação
└── docker-compose.yml
```

### Comandos Úteis
```bash
# Logs
docker-compose logs -f [service]

# Restart
docker-compose restart [service]

# Shell
docker-compose exec backend python manage.py shell

# Tests
docker-compose exec backend python manage.py test
```

---

## 📝 Contribuindo

1. Leia a documentação relevante
2. Crie uma branch: `git checkout -b feature/nome`
3. Commit: `git commit -m "feat: descrição"`
4. Push: `git push origin feature/nome`
5. Abra um Pull Request

---

## 📞 Suporte

### Documentação
- 📚 Docs completa nesta pasta
- 🔗 [README principal](../README.md)
- 📊 [Diagrama de arquitetura](./ARCHITECTURE_DIAGRAM.excalidraw.json)

### Issues
- 🐛 Bugs: GitHub Issues
- 💡 Features: GitHub Discussions
- ❓ Dúvidas: GitHub Discussions

---

## 📄 Licença

[Definir licença]

---

## 🔗 Links Úteis

- [MediaMTX Docs](https://github.com/bluenviron/mediamtx)
- [YOLOv8 Docs](https://docs.ultralytics.com/)
- [Django Docs](https://docs.djangoproject.com/)
- [React Docs](https://react.dev/)
- [HLS.js Docs](https://github.com/video-dev/hls.js/)

---

**Última atualização:** 2026-01-13  
**Versão da documentação:** 1.0.0  
**Mantido por:** VMS Team
