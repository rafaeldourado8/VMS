# 📹 VMS - Sistema de Monitoramento Inteligente para Prefeituras

## 🎯 Visão Geral

Sistema multi-tenant de monitoramento por vídeo com IA para detecção de placas veiculares (LPR) e busca retroativa em gravações, desenvolvido especificamente para atender prefeituras brasileiras.

---

## 🏛️ Modelo de Negócio

### Cliente: Prefeituras
Cada prefeitura opera como tenant isolado com:

- **Banco de dados dedicado** (1 DB por cidade)
- **Usuários centralizados** (gerenciados no DB administrativo)
- **Infraestrutura compartilhada** (serviços comuns)

---

## 📊 Capacidade por Prefeitura

### Câmeras Totais: até 1.000
- **Câmeras RTMP (Bullets):** até 1.000 unidades
  - Gravação 24/7 contínua
  - Sem processamento de IA
  - Apenas armazenamento

### Câmeras LPR: até 20
- **Câmeras RTSP (Alta Definição):** até 20 unidades
  - Gravação 24/7 contínua
  - IA em tempo real (YOLO + OCR)
  - Detecção automática de placas
  - Alertas instantâneos

### Sentinela: 1.000 câmeras
- **Busca retroativa com IA** em todas as câmeras
- Processa gravações históricas
- Reconstrói trajeto de veículos
- Busca por: placa, cor, tipo, marca, período

---

## 💾 Planos de Armazenamento

### Gravação Cíclica 24/7

| Plano | Retenção | Usuários | Recursos |
|-------|----------|----------|----------|
| **Basic** | 7 dias | 3 | Gravação + LPR |
| **Pro** | 15 dias | 5 | + Sentinela |
| **Premium** | 30 dias | 10 | + Relatórios + Analytics |

### Características
- ✅ Gravação contínua 24/7 durante todo o período do plano
- ✅ Notificação 1 dia antes da exclusão automática
- ✅ Clipes salvos manualmente são permanentes (não deletados)
- ✅ Replicação automática ao fim do ciclo

---

## 🤖 Inteligência Artificial

### 1. LPR Detection (Tempo Real)
**Onde:** Até 20 câmeras RTSP por prefeitura

**Tecnologia:**
- YOLOv8n (detecção de veículos)
- Fast-Plate-OCR (leitura de placas)
- PyTorch CPU-only

**Funcionalidades:**
- Detecção em tempo real
- Reconhecimento de placas brasileiras
- Alertas instantâneos
- Blacklist automática

### 2. Sentinela (Busca Retroativa)
**Onde:** Todas as 1.000 câmeras (gravações)

**Tecnologia:**
- YOLOv8n (detecção)
- AWS Rekognition (reconhecimento avançado)
- Processamento assíncrono

**Funcionalidades:**
- Busca por placa específica
- Busca por características (cor, tipo, marca)
- Reconstrução de trajeto entre câmeras
- Timeline com timestamps
- Exportação de evidências

---

## 🏗️ Arquitetura Multi-Tenant

### Isolamento de Dados
```
┌─────────────────────────────────────┐
│   DB Admin (Centralizado)           │
│   - Usuários                         │
│   - Autenticação                     │
│   - Configurações globais            │
└─────────────────────────────────────┘
           │
           ├─────────────────────────┐
           │                         │
┌──────────▼──────────┐   ┌─────────▼──────────┐
│  DB Cidade A        │   │  DB Cidade B       │
│  - Câmeras          │   │  - Câmeras         │
│  - Detecções        │   │  - Detecções       │
│  - Gravações        │   │  - Gravações       │
│  - Clipes           │   │  - Clipes          │
└─────────────────────┘   └────────────────────┘
```

### Vantagens
- ✅ Isolamento total de dados entre cidades
- ✅ Usuários podem ser transferidos entre cidades
- ✅ Backup e restore independentes
- ✅ Escalabilidade horizontal
- ✅ Conformidade com LGPD

---

## 🔄 Fluxo de Operação

### 1. Streaming + Gravação
```
Câmera → MediaMTX → [HLS Stream] → Frontend
                  ↓
              [Recording Service]
                  ↓
         Armazenamento Cíclico
         (7/15/30 dias)
```

### 2. Detecção em Tempo Real (LPR)
```
Câmera RTSP → Frame Extraction → YOLO → OCR → Backend
                                              ↓
                                         PostgreSQL
                                              ↓
                                         WebSocket
                                              ↓
                                         Frontend
```

### 3. Busca Retroativa (Sentinela)
```
Usuário → Query → Sentinela Service
                       ↓
                  Gravações (Storage)
                       ↓
                  YOLO + Rekognition
                       ↓
                  Resultados + Timeline
                       ↓
                  Frontend
```

---

## 🛠️ Stack Tecnológica

### Backend
- **Django 4.2** - API REST + Multi-tenant
- **PostgreSQL 15** - 1 DB por cidade + 1 admin
- **Redis 7** - Cache + Sessions
- **RabbitMQ 3.13** - Filas assíncronas
- **Celery** - Processamento background

### Frontend
- **React 18** - Interface responsiva
- **TypeScript** - Type safety
- **TailwindCSS** - Design system
- **Vite 5** - Build otimizado

### Streaming
- **MediaMTX** - Servidor HLS
- **FFmpeg** - Transcodificação
- **HLS.js** - Player web

### IA
- **YOLOv8n** - Detecção (CPU-only)
- **Fast-Plate-OCR** - Reconhecimento
- **AWS Rekognition** - Busca avançada (opcional)

### Infraestrutura
- **Docker Compose** - Orquestração
- **Prometheus** - Monitoramento
- **Grafana** - Dashboards

---

## 💰 Modelo de Custos (Estimativa)

### Por Prefeitura/Mês
- **Armazenamento:** $250-500 (dependendo do plano)
- **Banda:** $100-300 (streaming + gravação)
- **Processamento:** $200-400 (IA + backend)
- **Total:** ~$550-1.200/mês por cidade

### Otimizações Implementadas
- ✅ CPU-only (sem GPU) - 95% economia
- ✅ Gravação cíclica - 96% economia storage
- ✅ Cache de thumbnails - 95% economia banda
- ✅ Paginação + lazy loading - 99% economia recursos

---

## 🚀 Estrutura do Projeto

### Organização
```
VMS/
├── vms/                    # ← NOVO PROJETO (Clean Architecture)
│   ├── backend/
│   │   ├── domain/        # Entidades, Value Objects, Interfaces
│   │   ├── application/   # Use Cases, DTOs
│   │   ├── infrastructure/# Implementações (DB, Cache, IA)
│   │   └── presentation/  # API REST, WebSocket
│   ├── frontend/
│   │   ├── domain/        # Entidades
│   │   ├── application/   # Use Cases
│   │   ├── infrastructure/# HTTP, WebSocket
│   │   └── presentation/  # Components, Pages
│   └── docker-compose.yml
├── backend/               # Projeto antigo (manter como referência)
├── frontend/              # Projeto antigo (manter como referência)
└── .amazonq/
    └── prompts/
        ├── development-rules.md
        └── PROJECT_SUMMARY.md  # ← ESTE ARQUIVO
```

---

## 📋 Diferenciais Competitivos

✅ **Multi-tenant nativo** - Isolamento total por cidade  
✅ **IA dupla** - Tempo real (YOLO) + Retroativa (Rekognition)  
✅ **Escalável** - Até 1.000 câmeras por cidade  
✅ **Econômico** - CPU-only, sem GPU  
✅ **Flexível** - 3 planos de armazenamento  
✅ **Inteligente** - Sentinela reconstrói trajetos  
✅ **Compliant** - LGPD ready (dados isolados)  

---

## 🎯 Próximos Passos

### Desenvolvimento na pasta `vms/`
1. ✅ Criar estrutura Clean Architecture
2. ⏳ Implementar multi-tenant (DB por cidade)
3. ⏳ Sistema de planos (Basic/Pro/Premium)
4. ⏳ Gravação cíclica 24/7
5. ⏳ Notificações de expiração
6. ⏳ LPR em tempo real (20 câmeras)
7. ⏳ Sentinela (busca retroativa)

### Roadmap 30 Dias
- **Semana 1:** Core + Multi-tenant + Planos
- **Semana 2:** Streaming + Detection + Gravação
- **Semana 3:** Frontend + UX
- **Semana 4:** Sentinela + Deploy

---

**Projeto em desenvolvimento na pasta `vms/` 🚀**
