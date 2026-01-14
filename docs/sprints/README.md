# 🚀 Sprints - VMS até Deploy

Planejamento de sprints para completar o VMS até deploy em produção.

---

## 📋 Visão Geral

**Objetivo:** Sistema VMS completo, testado e em produção  
**Duração Total:** 4 sprints (8 semanas)  
**Status Atual:** Fase 0 completa, iniciando Sprint 1

---

## Sprint 1: Dashboard de Detecções (2 semanas)
**Período:** Semana 1-2  
**Objetivo:** Interface completa de visualização de detecções LPR

### Tasks
- [ ] API de detecções com filtros (câmera, placa, data, confiança)
- [ ] Interface DetectionsPage funcional (remover mock)
- [ ] Exportação CSV/Excel
- [ ] Integração LPR → Backend → Frontend em tempo real
- [ ] Testes E2E do fluxo completo

**Entregável:** Dashboard de detecções funcional com dados reais

---

## Sprint 2: Sistema de Blacklist (2 semanas)
**Período:** Semana 3-4  
**Objetivo:** Alertas automáticos para placas em blacklist

### Tasks
- [ ] Model Blacklist (placa, motivo, ativo, data_inicio, data_fim)
- [ ] CRUD de blacklist (API + Frontend)
- [ ] Sistema de alertas (email, push, webhook)
- [ ] Integração LPR → Verificação Blacklist → Alerta
- [ ] Interface de gerenciamento de blacklist
- [ ] Logs de alertas disparados

**Entregável:** Sistema de blacklist com alertas funcionando

---

## Sprint 3: Recording & Playback (2 semanas)
**Período:** Semana 5-6  
**Objetivo:** Gravação contínua e reprodução de vídeos

### Tasks
- [ ] Gravação cíclica (7/15/30 dias por plano)
- [ ] Storage management (limpeza automática)
- [ ] API de playback (busca por câmera + data)
- [ ] Player de vídeo com controles (play, pause, seek)
- [ ] Criação de clipes permanentes
- [ ] Timeline de eventos (detecções no vídeo)

**Entregável:** Sistema de gravação e playback funcional

---

## Sprint 4: Deploy & Produção (2 semanas)
**Período:** Semana 7-8  
**Objetivo:** Sistema em produção com monitoramento

### Tasks
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Docker Compose para produção
- [ ] Nginx + SSL (Let's Encrypt)
- [ ] Backup automático (PostgreSQL + Gravações)
- [ ] Monitoring (Prometheus + Grafana)
- [ ] Alertas de sistema (CPU, memória, disco)
- [ ] Documentação de deploy
- [ ] Testes de carga
- [ ] Rollback strategy

**Entregável:** VMS em produção com 99.9% uptime

---

## 📊 Métricas de Sucesso

### Sprint 1
- ✅ 100% das detecções aparecem no dashboard
- ✅ Filtros funcionam corretamente
- ✅ Exportação gera arquivos válidos

### Sprint 2
- ✅ Alertas disparados em <1s após detecção
- ✅ 0 falsos negativos (placa em blacklist não alertada)
- ✅ Logs completos de todos os alertas

### Sprint 3
- ✅ Gravação 24/7 sem perda de frames
- ✅ Playback com latência <2s
- ✅ Storage gerenciado automaticamente

### Sprint 4
- ✅ Deploy automatizado em <10min
- ✅ Uptime 99.9%
- ✅ Backup diário funcionando
- ✅ Alertas de sistema configurados

---

## 🔄 Próximas Fases (Pós-Deploy)

### Fase 5: Multi-Tenant (2 semanas)
- 1 banco por cidade
- Usuários transferíveis entre cidades
- Isolamento de dados

### Fase 6: Analytics & Relatórios (2 semanas)
- Relatórios de tráfego
- Estatísticas de detecções
- Dashboards executivos
- Exportação de dados

### Fase 7: Sentinela - Busca Retroativa (3 semanas)
- Busca em gravações por placa
- Busca por características do veículo (cor, tipo, marca)
- IA dupla: YOLO + Rekognition
- Timeline de resultados

---

## 📝 Notas

- Cada sprint tem review e retrospectiva
- Tasks podem ser ajustadas conforme necessidade
- Prioridade: funcionalidade > otimização
- Documentação obrigatória para cada feature
