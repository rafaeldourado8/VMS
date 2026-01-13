# 🐛 Relatórios de Bugs - VMS

Documentação estruturada de todos os bugs encontrados e corrigidos.

---

## 📋 Índice de Bugs

### Backend
- **[Session Timeout](./backend/session-timeout/)** - Sessões não expiravam com inatividade
  - Severidade: Alta
  - Status: ✅ Resolvido
  - Economia: $200/mês

### Frontend
- (Nenhum bug documentado ainda)

### Streaming
- (Nenhum bug documentado ainda)

### Detection
- (Nenhum bug documentado ainda)

### Infrastructure
- (Nenhum bug documentado ainda)

---

## 📊 Estatísticas

### Por Severidade
- Crítica: 0
- Alta: 1
- Média: 0
- Baixa: 0

### Por Status
- Abertos: 0
- Em investigação: 0
- Em correção: 0
- Resolvidos: 1

### Tempo Médio de Resolução
- MTTR: 3h 30min

---

## 🎯 Como Reportar um Bug

1. Criar pasta em `.amazonq/prompts/bugs/[COMPONENTE]/[BUG_NAME]/`
2. Usar [BUG_TEMPLATE.md](./BUG_TEMPLATE.md)
3. Criar os 6 arquivos obrigatórios:
   - DESCRIPTION.md
   - ROOT_CAUSE.md
   - SOLUTION.md
   - IMPACT.md
   - PREVENTION.md
   - TIMELINE.md
4. Adicionar ao índice acima

---

**Última atualização:** 2026-01-13
