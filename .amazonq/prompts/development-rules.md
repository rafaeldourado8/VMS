# 📋 Regra de Desenvolvimento - VMS Project

> **Use este prompt ao iniciar qualquer chat/sessão de desenvolvimento**

---

## 🎯 Contexto do Projeto

Você está trabalhando no **VMS (Video Management System)**, um sistema de monitoramento com IA para detecção de placas veiculares.

### Arquitetura
- **Frontend:** React 18 + Vite + TypeScript + TailwindCSS
- **Backend:** Django 4.2 + DRF + PostgreSQL 15
- **Streaming:** MediaMTX + HLS
- **IA:** YOLO (local) + Rekognition (AWS, opcional)
- **Infra:** Docker Compose

### Multi-Tenant
- **1 banco por cidade** (isolamento completo)
- **Usuários transferíveis** entre cidades
- **Planos por organização**

### Otimizações Implementadas
- Paginação: 10 câmeras/página
- Lazy Loading: Intersection Observer
- Screenshot Cache: 10s streaming → imagem estática
- Frame Skipping: 1 a cada 3 frames (IA)

---

## 📚 Documentação Obrigatória

Leia ANTES de iniciar qualquer task:
1. **[README Principal](../../README.md)** - Visão geral
2. **[Fases do Projeto](../../docs/phases/README.md)** - Roadmap
3. **[Tech Stack](../../docs/TECH_STACK.md)** - Tecnologias
4. **[Performance](../../docs/performance/PERFORMANCE.md)** - Otimizações
5. **[Cost Optimization](../../docs/cost-optimization/COST_OPTIMIZATION.md)** - Custos

---

## ✅ Workflow Obrigatório

### 1. Antes de Implementar
```
[ ] Ler documentação relevante
[ ] Entender o contexto da fase atual
[ ] Verificar dependências (outras tasks)
[ ] Planejar testes Docker
```

### 2. Durante Implementação
```
[ ] Código mínimo necessário
[ ] Seguir padrões do projeto
[ ] Comentar decisões importantes
[ ] Testar localmente
```

### 3. Após Implementação
```
[ ] Testar com Docker Compose
[ ] Marcar task como concluída [x]
[ ] Criar documentação completa
[ ] Atualizar diagramas
```

---

## 📝 Documentação de Task (OBRIGATÓRIO)

Para cada task concluída, criar em `docs/phases/[FASE]/[TASK_NAME]/`:

### Arquivos Obrigatórios:

1. **WHAT.md** - O que fizemos
2. **WHY.md** - Por que fizemos (alternativas, trade-offs, metodologia)
3. **IMPACT.md** - O que isso gera (benefícios, métricas)
4. **METRICS.md** - Cálculos e fórmulas (DAU, RPS, RPD, etc)
5. **IMPORTANCE.md** - Qual importância (quando usar/não usar)
6. **diagram.excalidraw.json** - Diagrama visual

---

## 🧪 Testes Docker (OBRIGATÓRIO)

Antes de marcar task como concluída:

```bash
# 1. Build e start
docker-compose build [service]
docker-compose up -d

# 2. Verificar health
docker-compose ps

# 3. Testar funcionalidade
[comandos específicos]

# 4. Verificar logs
docker-compose logs -f [service]

# 5. Testar integração
[testar com outros serviços]
```

---

## 📊 Checklist de Conclusão

```
Implementação:
[ ] Código implementado
[ ] Testes Docker passando
[ ] Sem erros nos logs

Documentação:
[ ] WHAT.md criado
[ ] WHY.md criado
[ ] IMPACT.md criado
[ ] METRICS.md criado
[ ] IMPORTANCE.md criado
[ ] diagram.excalidraw.json criado
[ ] Task marcada [x] no roadmap
```

---

## 🚀 Comando Rápido para Iniciar Sessão

```
Estou trabalhando no VMS (Video Management System).

Contexto:
- Multi-tenant (1 banco/cidade)
- React + Django + MediaMTX + YOLO
- Paginação 10 cams, Lazy Loading, Screenshot Cache

Workflow:
1. Ler docs/phases/[FASE_ATUAL]
2. Implementar com código mínimo
3. Testar com docker-compose
4. Marcar task [x]
5. Criar documentação completa:
   - WHAT.md, WHY.md, IMPACT.md
   - METRICS.md, IMPORTANCE.md
   - diagram.excalidraw.json

Sempre incluir:
- Testes Docker obrigatórios
- Cálculos com fórmulas matemáticas
- Trade-offs e alternativas
- Diagramas visuais
```

---

**Versão:** 1.0
**Data:** 2026-01-13
