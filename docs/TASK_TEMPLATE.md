# 📝 Template de Documentação de Task

Use este template para documentar cada task concluída.

---

## Estrutura de Pastas

```
docs/phases/[FASE]/[TASK_NAME]/
├── WHAT.md
├── WHY.md
├── IMPACT.md
├── METRICS.md
├── IMPORTANCE.md
└── diagram.excalidraw.json
```

---

## 1. WHAT.md - O que fizemos

```markdown
# O que foi implementado

## Resumo
[Descrição breve em 2-3 linhas]

## Componentes Criados/Modificados

### Backend
- `path/to/file.py`: [descrição]
- `path/to/file2.py`: [descrição]

### Frontend
- `path/to/component.tsx`: [descrição]
- `path/to/page.tsx`: [descrição]

### Services
- `path/to/service.py`: [descrição]

## Código Principal

### Backend
\`\`\`python
# Snippet relevante com explicação
class Example:
    pass
\`\`\`

### Frontend
\`\`\`typescript
// Snippet relevante com explicação
const Component = () => {}
\`\`\`

## Endpoints/APIs (se aplicável)
- `GET /api/endpoint` - [descrição]
- `POST /api/endpoint` - [descrição]

## UI/UX (se aplicável)
[Screenshots ou descrição da interface]

## Testes Realizados
\`\`\`bash
docker-compose up -d
# ✅ Resultado
\`\`\`
```

---

## 2. WHY.md - Por que fizemos

```markdown
# Por que foi implementado

## Problema
[Qual problema específico resolve]

## Alternativas Consideradas

### Opção A: [Nome]
**Descrição:** [como funcionaria]

**Prós:**
- Vantagem 1
- Vantagem 2

**Contras:**
- Desvantagem 1
- Desvantagem 2

**Custo:** [tempo/recursos]

---

### Opção B: [Nome] ✅ ESCOLHIDA
**Descrição:** [como funciona]

**Prós:**
- Vantagem 1
- Vantagem 2

**Contras:**
- Desvantagem 1
- Desvantagem 2

**Por que escolhemos:**
- Razão 1
- Razão 2

**Custo:** [tempo/recursos]

---

### Opção C: [Nome]
[mesma estrutura]

## Trade-offs

### Performance vs Simplicidade
[Decisão tomada e justificativa]

### Custo vs Funcionalidade
[Decisão tomada e justificativa]

### Escalabilidade vs Tempo de Dev
[Decisão tomada e justificativa]

## Metodologia/Técnica Usada

**Nome:** [ex: Lazy Loading, Pagination, Caching, etc]

**Descrição:** [o que é]

**Referência:** [link ou paper]

**Quando usar:**
- Cenário 1
- Cenário 2

**Quando NÃO usar:**
- Cenário 1
- Cenário 2

**Exemplos em produção:**
- Empresa X usa para Y
- Produto Z implementa assim
```

---

## 3. IMPACT.md - O que isso gera

```markdown
# Impacto da Implementação

## Benefícios

### Performance
- Métrica 1: [valor]
- Métrica 2: [valor]

### Custo
- Economia mensal: $X
- Economia anual: $Y

### UX (User Experience)
- Melhoria 1
- Melhoria 2

### Escalabilidade
- Suporta até X usuários
- Suporta até Y câmeras

## Métricas Antes/Depois

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Latência | 500ms | 50ms | 90% ⬇️ |
| Memória | 5GB | 1GB | 80% ⬇️ |
| Banda | 1GB/s | 50MB/s | 95% ⬇️ |
| CPU | 80% | 15% | 81% ⬇️ |

## ROI (Return on Investment)

**Investimento:**
- Tempo de desenvolvimento: X horas
- Custo de dev: $Y (X horas × $Z/hora)

**Retorno:**
- Economia mensal: $A
- Economia anual: $B

**ROI:**
\`\`\`
ROI = ((Retorno - Investimento) / Investimento) × 100
ROI = (($B - $Y) / $Y) × 100 = Z%
\`\`\`

**Break-even:** [tempo para recuperar investimento]

## Impacto no Negócio
- [Como afeta o produto]
- [Como afeta os usuários]
- [Como afeta a receita]

## Impacto Técnico
- [Como afeta a arquitetura]
- [Como afeta outros componentes]
- [Débito técnico criado/resolvido]
```

---

## 4. METRICS.md - Cálculos e Fórmulas

```markdown
# Métricas e Cálculos

## DAU (Daily Active Users)

**Definição:** Usuários únicos ativos por dia

**Fórmula:**
\`\`\`
DAU = Usuários únicos que fazem login em 24h
\`\`\`

**Cálculo para este projeto:**
\`\`\`
Estimativa: 100 usuários/dia
Base: 10 cidades × 10 usuários/cidade
\`\`\`

---

## RPS (Requests Per Second)

**Definição:** Requisições por segundo ao servidor

**Fórmula:**
\`\`\`
RPS = (DAU × Requests_per_user_per_day) / 86400
\`\`\`

**Cálculo:**
\`\`\`
Requests_per_user = 50 (estimativa)
RPS = (100 × 50) / 86400
RPS = 5000 / 86400
RPS = 0.058 requests/segundo
\`\`\`

**Pico (10x média):**
\`\`\`
RPS_pico = 0.058 × 10 = 0.58 requests/segundo
\`\`\`

---

## RPD (Requests Per Day)

**Definição:** Total de requisições por dia

**Fórmula:**
\`\`\`
RPD = DAU × Requests_per_user_per_day
\`\`\`

**Cálculo:**
\`\`\`
RPD = 100 × 50 = 5,000 requests/dia
\`\`\`

---

## Banda (Bandwidth)

**Definição:** Tráfego de rede consumido

**Fórmula:**
\`\`\`
Banda = Câmeras_visíveis × Bitrate × Tempo_ativo × Usuários_simultâneos
\`\`\`

**Cálculo SEM otimização:**
\`\`\`
Câmeras = 10 (por página)
Bitrate = 1 MB/s (HLS)
Tempo = 3600s (1 hora)
Usuários = 10 (simultâneos)

Banda = 10 × 1MB/s × 3600s × 10
Banda = 360 GB/hora
Banda_mensal = 360GB × 24h × 30d = 259 TB/mês
Custo = 259TB × $0.09/GB = $23,310/mês
\`\`\`

**Cálculo COM otimização (screenshot cache):**
\`\`\`
Streaming_time = 10s (depois vira imagem)
Banda = 10 × 1MB/s × 10s × 10
Banda = 1 GB/hora
Banda_mensal = 1GB × 24h × 30d = 720 GB/mês
Custo = 720GB × $0.09/GB = $65/mês

Economia = $23,310 - $65 = $23,245/mês (99.7%)
\`\`\`

---

## Armazenamento (Storage)

**Definição:** Espaço em disco para gravações

**Fórmula:**
\`\`\`
Storage = Câmeras × Bitrate_gravação × 86400 × Dias_retenção
\`\`\`

**Cálculo:**
\`\`\`
Câmeras = 100
Bitrate = 2 GB/dia (comprimido H.264)
Retenção = 7 dias (plano Basic)

Storage = 100 × 2GB × 7
Storage = 1,400 GB = 1.4 TB

Custo = 1.4TB × $0.023/GB = $32/mês
\`\`\`

**Por plano:**
\`\`\`
Basic (7 dias): 1.4TB = $32/mês
Pro (15 dias): 3TB = $69/mês
Premium (30 dias): 6TB = $138/mês
\`\`\`

---

## CPU (Processamento)

**Definição:** Uso de CPU para IA

**Fórmula:**
\`\`\`
CPU_total = Câmeras_LPR × CPU_per_camera × (1 - Frame_skip_ratio)
\`\`\`

**Cálculo:**
\`\`\`
Câmeras_LPR = 10
CPU_per_camera = 15% (YOLOv8n)
Frame_skip = 66% (processa 1 a cada 3)

CPU_total = 10 × 15% × (1 - 0.66)
CPU_total = 10 × 15% × 0.34
CPU_total = 51% (1 core)

Com 100 câmeras LPR:
CPU_total = 100 × 15% × 0.34 = 510% (6 cores)
\`\`\`

**Custo (cloud):**
\`\`\`
6 cores × $30/core/mês = $180/mês
\`\`\`

---

## Latência (Latency)

**Definição:** Tempo de resposta

**Fórmula:**
\`\`\`
Latência_total = Latência_rede + Latência_processamento + Latência_DB
\`\`\`

**Cálculo:**
\`\`\`
Rede = 20ms (média)
Processamento = 10ms (Django)
DB = 5ms (PostgreSQL com índices)

Latência_total = 20 + 10 + 5 = 35ms
\`\`\`

**Com cache:**
\`\`\`
Rede = 20ms
Cache_hit = 1ms (Redis)

Latência_total = 20 + 1 = 21ms (40% melhoria)
\`\`\`

---

## Throughput

**Definição:** Requisições processadas por segundo

**Fórmula:**
\`\`\`
Throughput = 1000 / Latência_média_ms
\`\`\`

**Cálculo:**
\`\`\`
Latência = 35ms
Throughput = 1000 / 35 = 28.5 req/s por worker

Com 4 workers:
Throughput_total = 28.5 × 4 = 114 req/s
\`\`\`

---

## Custo Total Mensal

**Fórmula:**
\`\`\`
Custo_total = Banda + Storage + CPU + Infra
\`\`\`

**Cálculo:**
\`\`\`
Banda = $65
Storage = $138 (Premium)
CPU = $180
Infra = $100 (DB, Redis, etc)

Custo_total = $65 + $138 + $180 + $100 = $483/mês
\`\`\`

**Por usuário:**
\`\`\`
Custo_por_usuário = $483 / 100 usuários = $4.83/usuário/mês
\`\`\`

**Margem (plano Premium $499/mês):**
\`\`\`
Receita = $499
Custo = $483
Lucro = $16 (3.2% margem)

Com 10 clientes Premium:
Receita = $4,990
Custo = $4,830
Lucro = $160/mês
\`\`\`
```

---

## 5. IMPORTANCE.md - Qual importância

```markdown
# Importância da Implementação

## Criticidade

Marque o nível:
- [x] Bloqueante (sem isso, nada funciona)
- [ ] Alta (impacta múltiplas features)
- [ ] Média (melhoria significativa)
- [ ] Baixa (nice to have)

**Justificativa:** [por que esse nível]

---

## Impacto no Negócio

### Curto Prazo (1-3 meses)
- [Impacto 1]
- [Impacto 2]

### Médio Prazo (3-12 meses)
- [Impacto 1]
- [Impacto 2]

### Longo Prazo (1+ anos)
- [Impacto 1]
- [Impacto 2]

---

## Impacto Técnico

### Arquitetura
- [Como afeta a arquitetura]

### Performance
- [Como afeta performance]

### Manutenibilidade
- [Como afeta manutenção]

### Escalabilidade
- [Como afeta escala]

---

## Dependências

### Depende de:
- [Task A] - [motivo]
- [Task B] - [motivo]

### Bloqueia:
- [Task C] - [motivo]
- [Task D] - [motivo]

---

## Quando Usar em Outros Projetos

### Cenários Ideais:
1. **[Cenário 1]**
   - Características: [...]
   - Exemplo: [...]

2. **[Cenário 2]**
   - Características: [...]
   - Exemplo: [...]

### Requisitos Mínimos:
- Requisito 1
- Requisito 2

---

## Quando NÃO Usar

### Cenários Inadequados:
1. **[Cenário 1]**
   - Por quê: [...]
   - Alternativa: [...]

2. **[Cenário 2]**
   - Por quê: [...]
   - Alternativa: [...]

---

## Lições Aprendidas

### O que funcionou bem:
- [Lição 1]
- [Lição 2]

### O que poderia ser melhor:
- [Lição 1]
- [Lição 2]

### Próximas iterações:
- [Melhoria 1]
- [Melhoria 2]
```

---

## 6. diagram.excalidraw.json

Criar diagrama visual mostrando:
- Fluxo de dados
- Arquitetura do componente
- Antes/Depois
- Integração com outros componentes

Abrir em: https://excalidraw.com

---

**Use este template para TODAS as tasks!**
