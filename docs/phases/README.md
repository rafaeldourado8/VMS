# 🚀 VMS - Roadmap de Desenvolvimento

> **Arquitetura Multi-Tenant**: Cada cidade = banco de dados único
> **Usuários transferíveis**: Usuários podem ser movidos entre cidades
> **IA Dupla**: YOLO (local) + Rekognition (AWS, opcional)

---

## 📋 Índice de Fases

### ✅ [Fase 0: Base Implementada](./PHASE_0_BASE.md)
- Streaming (MediaMTX + HLS)
- Backend API (Django)
- Frontend (React)
- LPR Detection (YOLO + OCR)
- Paginação de câmeras

### 🔄 [Fase 1: Dashboard de Detecções](./PHASE_1_DETECTIONS.md)
**Tempo:** 1-2 semanas
- API de detecções completa
- Interface de visualização
- Filtros e exportação
- Integração LPR → Backend

### 🚨 [Fase 2: Sistema de Blacklist](./PHASE_2_BLACKLIST.md)
**Tempo:** 1 semana
- CRUD de blacklist
- Alertas automáticos
- Notificações em tempo real
- WebSocket

### 🎬 [Fase 3: Recording & Playback](./PHASE_3_RECORDING.md)
**Tempo:** 2 semanas
- Gravação cíclica por plano
- Timeline de reprodução
- Criação de clipes permanentes
- Player com controles

### 🔍 [Fase 4: Sentinela (Busca Retroativa)](./PHASE_4_SENTINELA.md)
**Tempo:** 2-3 semanas
- IA dedicada para gravações
- Busca por placa/cor/tipo
- YOLO + Rekognition
- Processamento assíncrono

### 👥 [Fase 5: Multi-Tenant & Usuários](./PHASE_5_MULTITENANT.md)
**Tempo:** 2 semanas
- Banco por cidade
- Transferência de usuários
- Sistema de planos
- Permissões e limites

### 📊 [Fase 6: Analytics & Relatórios](./PHASE_6_ANALYTICS.md)
**Tempo:** 1-2 semanas
- Dashboard analítico
- Relatórios automatizados
- Estatísticas avançadas
- Exportação de dados

---

## 🏗️ Arquitetura Geral

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  Câmeras | Detecções | Blacklist | Playback | Sentinela │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/WebSocket
┌────────────────────────▼────────────────────────────────┐
│                 BACKEND (Django REST)                    │
│  Multi-Tenant Router → Database por Cidade              │
└────────┬───────────┬───────────┬──────────┬─────────────┘
         │           │           │          │
    ┌────▼────┐ ┌───▼────┐ ┌────▼─────┐ ┌─▼────────┐
    │   LPR   │ │Sentinela│ │Recording│ │MediaMTX  │
    │  YOLO   │ │IA Busca │ │ Service │ │Streaming │
    └─────────┘ └─────────┘ └──────────┘ └──────────┘
```

---

## 📊 Estado Atual

### ✅ Implementado
- [x] Streaming HLS (MediaMTX)
- [x] Backend Django REST
- [x] Frontend React + Vite
- [x] LPR Detection (YOLO + OCR)
- [x] Paginação (10 câmeras/página)
- [x] Lazy loading + Screenshot cache
- [x] PostgreSQL, Redis, RabbitMQ
- [x] Docker Compose

### 🔄 Em Progresso
- [ ] Dashboard de detecções
- [ ] Sistema de blacklist
- [ ] Recording service

### ❌ Não Iniciado
- [ ] Playback & Timeline
- [ ] Sentinela (busca retroativa)
- [ ] Multi-tenant
- [ ] Sistema de planos
- [ ] Analytics

---

## 🎯 Prioridades

### Sprint 1-2: Detecções
```
Objetivo: Interface completa para visualizar detecções
- Backend: API de detecções
- Frontend: Página com filtros
- Exportação: CSV/Excel
- Integração: LPR → Backend → Frontend
```

### Sprint 3: Blacklist
```
Objetivo: Alertas automáticos para placas específicas
- Backend: CRUD + Verificação
- Frontend: Página + Notificações
- WebSocket: Alertas em tempo real
```

### Sprint 4-5: Recording
```
Objetivo: Gravação cíclica e reprodução
- Service: Gravação com cleanup
- Backend: API de timeline/clipes
- Frontend: Player + Timeline
```

### Sprint 6-8: Sentinela
```
Objetivo: Busca retroativa em gravações
- Service: IA dedicada
- Backend: API de busca
- Frontend: Interface de busca
- IA: YOLO + Rekognition
```

### Sprint 9-10: Multi-Tenant
```
Objetivo: Banco por cidade + transferência de usuários
- Backend: Router multi-tenant
- Models: Organization/City
- Migração: Dados existentes
```

### Sprint 11-12: Analytics
```
Objetivo: Dashboard e relatórios
- Backend: APIs de estatísticas
- Frontend: Gráficos e cards
- Relatórios: Email automático
```

---

## 🔧 Comandos de Teste

### Teste Completo
```bash
docker-compose up -d
docker-compose ps  # Verificar todos healthy
curl http://localhost:8000/health
curl http://localhost:5173
```

### Por Fase
```bash
# Fase 1 - Detecções
curl http://localhost:8000/api/detections/
curl http://localhost:8000/api/detections/stats/

# Fase 2 - Blacklist
curl http://localhost:8000/api/blacklist/
curl http://localhost:8000/api/alerts/

# Fase 3 - Recording
curl http://localhost:8003/health
curl http://localhost:8000/api/recordings/timeline/1/

# Fase 4 - Sentinela
curl http://localhost:8004/health
curl -X POST http://localhost:8004/search
```

---

## 📝 Observações Importantes

### Multi-Tenant
- **1 banco por cidade** (isolamento completo)
- **Usuários transferíveis** entre cidades
- **Planos por organização** (não por cidade)

### IA
- **YOLO**: Local, gratuito, sempre disponível
- **Rekognition**: AWS, opcional, backup/validação
- **Sem ROI**: Processamento de frame completo

### Streaming
- **HLS**: Mantido (não usar LL-HLS)
- **Paginação**: 10 câmeras por página
- **Lazy loading**: Intersection Observer
- **Cache**: Screenshot após 10s

---

**Próximo passo:** [Fase 1 - Dashboard de Detecções](./PHASE_1_DETECTIONS.md)
