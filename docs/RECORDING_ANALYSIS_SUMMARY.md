# Análise do Sistema de Gravação - Resumo Executivo

## 📋 Componentes Analisados

### Microserviços FastAPI

| Serviço | Porta | Responsabilidade | Status |
|---------|-------|------------------|--------|
| **recorder** | - | Grava streams RTSP em segmentos de 60s | ✅ Funcional |
| **retention_cleanup** | - | Limpeza FIFO de gravações antigas (1h) | ✅ Funcional |
| **recording** | 8006 | API para listar/validar gravações | ✅ Funcional |
| **storage** | 8003 | Indexa segmentos no PostgreSQL | ✅ Funcional |
| **timeline** | 8007 | Constrói timeline com gaps | ✅ Funcional |

### Django Apps

| App | Responsabilidade | Status |
|-----|------------------|--------|
| **recordings** | Modelo de gravações + API REST | ✅ Funcional |
| **timeline** | Políticas de retenção + auditoria | ✅ Funcional |

---

## ⚠️ Problemas Identificados

### 1. **Falta de Orquestração**
- Serviços não se comunicam diretamente
- Sem coordenação entre RECORDER → STORAGE → TIMELINE
- Cleanup não notifica Timeline automaticamente
- **Impacto:** Timeline pode ficar desatualizado

### 2. **Duplicação de Lógica**
- Django e FastAPI têm lógicas similares de scan
- Storage e Timeline fazem scan independente
- **Impacto:** Desperdício de recursos

### 3. **Falta de Sincronização**
- Timeline pode ter cache desatualizado
- Storage pode ter índices órfãos
- **Impacto:** Dados inconsistentes

### 4. **Sem Event Bus**
- Comunicação ponto-a-ponto
- Difícil rastrear fluxo de dados
- **Impacto:** Difícil debugar e monitorar

---

## ✅ Solução Implementada

### **Recording Orchestrator** (FastAPI - Port 8010)

Serviço central que coordena todos os componentes:

#### Funcionalidades

1. **Event Bus (Redis Pub/Sub)**
   - Eventos: `recording.created`, `recording.deleted`, `recording.indexed`
   - Serviços subscrevem e reagem automaticamente

2. **Coordenação de Cleanup**
   - Deleta arquivos
   - Atualiza Storage
   - Reindex Timeline
   - Notifica Django
   - Tudo em sequência coordenada

3. **Health Monitoring**
   - Verifica saúde de todos os serviços
   - Latência de resposta
   - Auto-recovery

4. **Timeline Proxy**
   - Centraliza acesso à Timeline
   - Cache inteligente
   - Reindexação sob demanda

#### Endpoints Principais

```
GET  /health                      - Status do orquestrador
GET  /services/health             - Status de todos os serviços
POST /events/publish              - Publica evento
POST /cleanup/{camera_id}         - Orquestra cleanup
GET  /timeline/{camera_id}        - Proxy para timeline
GET  /timeline/{camera_id}/blocks - Blocos de gravação
POST /recording/created           - Webhook de nova gravação
```

---

## 🎯 Arquitetura Final

```
┌─────────────────────────────────────────────────────────────┐
│              RECORDING ORCHESTRATOR (Port 8010)              │
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Event Bus  │  │   Health    │  │   Cleanup   │         │
│  │ Redis Pub/Sub│  │   Monitor   │  │ Coordinator │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    RECORDER     │  │     STORAGE     │  │    TIMELINE     │
│  - Grava vídeos │  │  - Indexa DB    │  │  - Constrói     │
│  - Notifica     │  │  - Subscreve    │  │    timeline     │
│    eventos      │  │    eventos      │  │  - Cache        │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                    ┌─────────────────┐
                    │   /recordings   │
                    │  (File System)  │
                    └─────────────────┘
```

---

## 📊 Fluxos Coordenados

### Fluxo 1: Nova Gravação
```
RECORDER cria arquivo
    ↓
POST /recording/created
    ↓
Orchestrator publica evento
    ↓
┌───────────┴───────────┐
▼                       ▼
STORAGE scan      TIMELINE reindex
```

### Fluxo 2: Cleanup
```
POST /cleanup/{camera_id}
    ↓
Orchestrator coordena:
    ↓
1. Deleta arquivos
2. Publica eventos
3. Reindex Timeline
4. Notifica Django
    ↓
Sistema sincronizado
```

### Fluxo 3: Query Timeline
```
Frontend → Orchestrator → Timeline
              ↓
        Cache hit/miss
              ↓
        Return blocks
              ↓
    Player com barra de progresso
```

---

## 🚀 Próximos Passos

### 1. Integração do Orchestrator
- [ ] Adicionar ao docker-compose.yml
- [ ] Configurar variáveis de ambiente
- [ ] Testar health checks

### 2. Modificar RECORDER
- [ ] Adicionar webhook para notificar eventos
- [ ] Integrar com Orchestrator

### 3. Modificar STORAGE
- [ ] Subscrever eventos do Redis
- [ ] Reagir a eventos de cleanup

### 4. Frontend - Timeline Player
- [ ] Criar componente TimelinePlayer
- [ ] Barra de progresso com gaps
- [ ] Integrar com Orchestrator API

### 5. Testes
- [ ] Testar fluxo completo de gravação
- [ ] Testar cleanup coordenado
- [ ] Testar sincronização de timeline

---

## 📁 Arquivos Criados

1. **`docs/RECORDING_ARCHITECTURE.md`**
   - Documentação completa da arquitetura
   - Papel de cada serviço
   - Modelos de dados
   - Fluxos de comunicação

2. **`services/orchestrator/main.py`**
   - Serviço orquestrador FastAPI
   - Event Bus Redis
   - Coordenação de cleanup
   - Health monitoring

3. **`services/orchestrator/requirements.txt`**
   - Dependências Python

4. **`services/orchestrator/Dockerfile`**
   - Container Docker

5. **`docs/ORCHESTRATOR_INTEGRATION.md`**
   - Guia de integração
   - Endpoints documentados
   - Exemplos de uso
   - Configuração Docker

---

## 💡 Benefícios da Solução

### Antes
- ❌ Serviços desconectados
- ❌ Timeline desatualizada
- ❌ Cleanup sem coordenação
- ❌ Difícil debugar

### Depois
- ✅ Orquestração centralizada
- ✅ Event-driven architecture
- ✅ Sincronização automática
- ✅ Monitoramento integrado
- ✅ Fácil rastreabilidade

---

## 🎬 Objetivo Final: Timeline Player

Com o Orchestrator, agora é possível construir:

```typescript
// Frontend React
const TimelinePlayer = ({ cameraId }) => {
  const { data: blocks } = useQuery(
    ['timeline', cameraId],
    () => fetch(`/orchestrator/timeline/${cameraId}/blocks`)
  );

  return (
    <div>
      <VideoPlayer />
      <ProgressBar blocks={blocks} showGaps={true} />
    </div>
  );
};
```

**Features:**
- Barra de progresso com segmentos
- Gaps visíveis (períodos sem gravação)
- Seek para timestamp específico
- Indicador de cobertura (%)
