# 🐛 Template de Relatório de Bug

Use este template para documentar bugs encontrados no sistema.

---

## Estrutura de Pastas

```
.amazonq/prompts/bugs/
├── frontend/
│   └── [BUG_NAME]/
├── backend/
│   └── [BUG_NAME]/
├── streaming/
│   └── [BUG_NAME]/
├── detection/
│   └── [BUG_NAME]/
└── infrastructure/
    └── [BUG_NAME]/
```

Cada bug deve ter sua própria pasta com os seguintes arquivos:

---

## Arquivos Obrigatórios

### 1. `DESCRIPTION.md` - Descrição do Bug

```markdown
# 🐛 [Nome do Bug]

## Resumo
[Descrição breve em 1-2 linhas]

## Severidade
- [ ] Crítica (sistema quebrado)
- [ ] Alta (funcionalidade importante afetada)
- [ ] Média (funcionalidade secundária afetada)
- [ ] Baixa (cosmético ou edge case)

## Componente Afetado
- Serviço: [backend/frontend/streaming/etc]
- Arquivo: [caminho do arquivo]
- Função/Componente: [nome específico]

## Ambiente
- OS: [Windows/Linux/Mac]
- Browser: [se aplicável]
- Docker: [versão]
- Versão do código: [commit hash]

## Descrição Detalhada
[Explicação completa do problema]

## Como Reproduzir
1. Passo 1
2. Passo 2
3. Passo 3

## Comportamento Esperado
[O que deveria acontecer]

## Comportamento Atual
[O que está acontecendo]

## Screenshots/Logs
[Se aplicável]

## Impacto
- Usuários afetados: [número ou %]
- Frequência: [sempre/às vezes/raro]
- Workaround disponível: [sim/não]
```

---

### 2. `ROOT_CAUSE.md` - Causa Raiz

```markdown
# 🔍 Análise de Causa Raiz

## Investigação

### Hipóteses Iniciais
1. [Hipótese 1]
2. [Hipótese 2]
3. [Hipótese 3]

### Testes Realizados
- [ ] Teste 1: [resultado]
- [ ] Teste 2: [resultado]
- [ ] Teste 3: [resultado]

## Causa Raiz Identificada

### Problema Principal
[Descrição da causa raiz]

### Por que aconteceu?
[Explicação técnica]

### Código Problemático
\`\`\`[linguagem]
// Código que causa o bug
\`\`\`

### Por que não foi detectado antes?
- [Razão 1]
- [Razão 2]

## Análise dos 5 Porquês

1. **Por quê?** [Problema inicial]
2. **Por quê?** [Causa do problema]
3. **Por quê?** [Causa da causa]
4. **Por quê?** [Causa mais profunda]
5. **Por quê?** [Causa raiz]

## Fatores Contribuintes
- [Fator 1]
- [Fator 2]
```

---

### 3. `SOLUTION.md` - Solução

```markdown
# ✅ Solução Implementada

## Resumo da Correção
[Descrição breve da solução]

## Código Corrigido

### Antes
\`\`\`[linguagem]
// Código com bug
\`\`\`

### Depois
\`\`\`[linguagem]
// Código corrigido
\`\`\`

## Arquivos Modificados
- `path/to/file1.ext` - [descrição da mudança]
- `path/to/file2.ext` - [descrição da mudança]

## Testes Realizados
\`\`\`bash
# Comandos de teste
docker-compose up -d
# Resultado: ✅ Passou
\`\`\`

## Validação
- [ ] Bug não ocorre mais
- [ ] Testes automatizados passam
- [ ] Sem regressões
- [ ] Performance mantida
- [ ] Documentação atualizada

## Deploy
- Data: [YYYY-MM-DD]
- Commit: [hash]
- Branch: [nome]
```

---

### 4. `IMPACT.md` - Impacto

```markdown
# 📊 Impacto do Bug

## Impacto Antes da Correção

### Usuários
- Afetados: [número ou %]
- Reclamações: [quantidade]
- Tickets abertos: [quantidade]

### Performance
- Latência: [aumento]
- CPU: [uso extra]
- Memória: [vazamento]
- Banda: [desperdício]

### Custos
- Custo extra: $[valor]/mês
- Tempo perdido: [horas]
- Suporte: [horas de atendimento]

## Impacto Após Correção

### Melhorias
- Performance: [melhoria]
- Estabilidade: [melhoria]
- UX: [melhoria]

### Economia
- Custo economizado: $[valor]/mês
- Tempo economizado: [horas]

## Métricas

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| [Métrica 1] | [valor] | [valor] | [%] |
| [Métrica 2] | [valor] | [valor] | [%] |
```

---

### 5. `PREVENTION.md` - Prevenção

```markdown
# 🛡️ Prevenção de Recorrência

## Medidas Preventivas Implementadas

### 1. Testes Automatizados
\`\`\`[linguagem]
// Teste que previne o bug
test('should not [bug behavior]', () => {
  // ...
})
\`\`\`

### 2. Validações Adicionadas
- [Validação 1]
- [Validação 2]

### 3. Monitoramento
- Alerta: [descrição]
- Métrica: [qual métrica monitorar]
- Threshold: [valor de alerta]

### 4. Documentação
- [Documentação atualizada]
- [Guia criado]

## Lições Aprendidas

### O que funcionou bem
- [Lição 1]
- [Lição 2]

### O que pode melhorar
- [Melhoria 1]
- [Melhoria 2]

## Checklist de Prevenção

Para evitar bugs similares no futuro:
- [ ] Adicionar testes de edge cases
- [ ] Revisar código relacionado
- [ ] Atualizar documentação
- [ ] Treinar equipe
- [ ] Adicionar monitoramento
- [ ] Revisar processo de QA
```

---

### 6. `TIMELINE.md` - Linha do Tempo

```markdown
# ⏱️ Timeline do Bug

## Cronologia

### Descoberta
- **Data:** [YYYY-MM-DD HH:MM]
- **Reportado por:** [nome/sistema]
- **Como:** [monitoramento/usuário/teste]

### Investigação
- **Início:** [YYYY-MM-DD HH:MM]
- **Duração:** [tempo]
- **Responsável:** [nome]

### Correção
- **Início:** [YYYY-MM-DD HH:MM]
- **Fim:** [YYYY-MM-DD HH:MM]
- **Duração:** [tempo]
- **Responsável:** [nome]

### Deploy
- **Data:** [YYYY-MM-DD HH:MM]
- **Ambiente:** [dev/staging/prod]
- **Validação:** [tempo]

### Resolução
- **Data:** [YYYY-MM-DD HH:MM]
- **Tempo total:** [desde descoberta até resolução]

## Métricas de Resposta

- **MTTD** (Mean Time To Detect): [tempo]
- **MTTI** (Mean Time To Investigate): [tempo]
- **MTTF** (Mean Time To Fix): [tempo]
- **MTTD** (Mean Time To Deploy): [tempo]
- **MTTR** (Mean Time To Resolve): [tempo total]
```

---

## Exemplo Real: Timeout de Sessão

Ver: `.amazonq/prompts/bugs/backend/session-timeout/`

---

**Use este template para TODOS os bugs!**
