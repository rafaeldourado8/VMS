# 📊 PLANO DE CAPACIDADE - VMS

## 🎯 CAPACIDADE ATUAL (Single Instance)

### Hardware Alocado
```
MediaMTX:     3 CPU cores / 3 GB RAM
Recorder:     2 CPU cores / 2 GB RAM  
Backend:      1 CPU core  / 1 GB RAM
Frontend:     0.5 CPU     / 512 MB RAM
PostgreSQL:   1 CPU core  / 1 GB RAM
Redis:        0.5 CPU     / 512 MB RAM
```

### Capacidade Técnica

| Recurso | Capacidade | Utilização Atual | Margem |
|---------|------------|------------------|--------|
| **Câmeras (gravação 24/7)** | 15-20 | 0 | 100% |
| **Viewers simultâneos** | 50-80 | 0 | 100% |
| **Detecções LPR/dia** | 50,000 | 0 | 100% |
| **Storage (7 dias)** | 2.5 TB | 0 GB | 100% |
| **Bandwidth saída** | 200 Mbps | 0 | 100% |

---

## 👥 MÉTRICAS DE USUÁRIO

### DAU (Daily Active Users)

**Definição de usuário ativo:**
- Login no sistema
- Visualização de pelo menos 1 câmera
- Período: últimas 24h

**Capacidade por cenário:**

| Cenário | DAU | Viewers Simultâneos | Câmeras | Status |
|---------|-----|---------------------|---------|--------|
| **Atual** | 0 | 0 | 0 | ✅ Ocioso |
| **Pequeno** | 5-10 | 3-5 | 5-10 | ✅ Confortável |
| **Médio** | 20-30 | 10-15 | 15-20 | ✅ Ideal |
| **Grande** | 50-80 | 30-50 | 20-25 | ⚠️ Limite |
| **Máximo** | 100 | 80 | 25-30 | 🔴 Saturado |

### Padrão de Uso Típico

```
Usuário médio:
- 2-3 logins/dia
- 15-30 min de visualização
- 3-5 câmeras diferentes
- 2-3 buscas de detecção

Pico de acesso:
- Horário comercial: 8h-18h
- Pico: 10h-12h e 14h-16h
- Fator de pico: 3x média
```

---

## 📈 CENÁRIOS DE CRESCIMENTO

### Cenário 1: Startup (0-6 meses)
```
Câmeras: 5-10
DAU: 5-15
MAU: 10-30
Viewers simultâneos: 3-8
Detecções/dia: 5,000-10,000

Recursos necessários:
- CPU: 30-40%
- RAM: 40-50%
- Storage: 500 GB
- Bandwidth: 20-40 Mbps

Status: ✅ ATUAL SUPORTA
```

### Cenário 2: Crescimento (6-12 meses)
```
Câmeras: 15-20
DAU: 20-40
MAU: 50-100
Viewers simultâneos: 15-25
Detecções/dia: 20,000-30,000

Recursos necessários:
- CPU: 60-75%
- RAM: 70-80%
- Storage: 2 TB
- Bandwidth: 80-120 Mbps

Status: ✅ ATUAL SUPORTA
```

### Cenário 3: Escala (12-24 meses)
```
Câmeras: 30-50
DAU: 50-100
MAU: 150-300
Viewers simultâneos: 40-80
Detecções/dia: 50,000-80,000

Recursos necessários:
- CPU: 100%+ (UPGRADE)
- RAM: 100%+ (UPGRADE)
- Storage: 5 TB
- Bandwidth: 200-400 Mbps

Status: 🔴 REQUER UPGRADE
Solução: Multi-instância (3-5 MediaMTX)
```

### Cenário 4: Enterprise (24+ meses)
```
Câmeras: 100-500
DAU: 200-500
MAU: 500-1500
Viewers simultâneos: 150-400
Detecções/dia: 200,000-500,000

Recursos necessários:
- CPU: 50-75 cores
- RAM: 50-100 GB
- Storage: 50-100 TB
- Bandwidth: 1-2 Gbps

Status: 🔴 REQUER KUBERNETES
Solução: Cluster K8s (20-30 pods)
```

---

## 💰 MODELO DE NEGÓCIO

### Pricing Tiers

**Tier 1: Starter**
```
Câmeras: até 5
Usuários: até 3
Retenção: 7 dias
Preço: R$ 299/mês
Margem: 70%
```

**Tier 2: Professional**
```
Câmeras: até 15
Usuários: até 10
Retenção: 15 dias
Preço: R$ 799/mês
Margem: 65%
```

**Tier 3: Business**
```
Câmeras: até 30
Usuários: até 30
Retenção: 30 dias
Preço: R$ 1,999/mês
Margem: 60%
```

**Tier 4: Enterprise**
```
Câmeras: 50+
Usuários: ilimitados
Retenção: customizada
Preço: sob consulta
Margem: 50%
```

### Custo por Cliente

**Tier 1 (5 câmeras):**
```
Infra: R$ 50/mês
Storage: R$ 20/mês
Bandwidth: R$ 10/mês
Suporte: R$ 10/mês
Total: R$ 90/mês
Receita: R$ 299/mês
Lucro: R$ 209/mês (70%)
```

**Tier 2 (15 câmeras):**
```
Infra: R$ 150/mês
Storage: R$ 80/mês
Bandwidth: R$ 40/mês
Suporte: R$ 30/mês
Total: R$ 300/mês
Receita: R$ 799/mês
Lucro: R$ 499/mês (62%)
```

---

## 🎯 CAPACIDADE POR TIER

### Servidor Atual (Single Instance)

| Tier | Clientes | Câmeras Total | DAU Total | Status |
|------|----------|---------------|-----------|--------|
| **Starter** | 4 | 20 | 12 | ✅ Suporta |
| **Professional** | 1-2 | 15-30 | 10-20 | ✅ Suporta |
| **Business** | 1 | 30 | 30 | ⚠️ Limite |
| **Mix** | 2 Starter + 1 Pro | 25 | 25 | ✅ Ideal |

### Receita Máxima (Single Instance)

**Cenário Otimizado:**
```
2x Starter:      R$ 598/mês
1x Professional: R$ 799/mês
Total:           R$ 1,397/mês
Custo infra:     R$ 500/mês
Lucro:           R$ 897/mês (64%)

Câmeras: 25
DAU: 25
Utilização: 75%
```

---

## 📊 PROJEÇÃO DE CRESCIMENTO

### Ano 1 (Meses 1-12)

| Mês | Clientes | Câmeras | DAU | MRR | Infra |
|-----|----------|---------|-----|-----|-------|
| 1 | 1 | 5 | 3 | R$ 299 | R$ 500 |
| 3 | 3 | 15 | 10 | R$ 897 | R$ 500 |
| 6 | 5 | 25 | 20 | R$ 1,995 | R$ 500 |
| 12 | 8 | 40 | 35 | R$ 3,990 | R$ 1,500 |

**Mês 12: UPGRADE necessário (multi-instância)**

### Ano 2 (Meses 13-24)

| Mês | Clientes | Câmeras | DAU | MRR | Infra |
|-----|----------|---------|-----|-----|-------|
| 15 | 15 | 80 | 60 | R$ 7,985 | R$ 2,500 |
| 18 | 25 | 150 | 100 | R$ 14,975 | R$ 4,000 |
| 24 | 40 | 250 | 180 | R$ 29,960 | R$ 8,000 |

**Mês 24: Migração para Kubernetes**

---

## 🚀 ROADMAP DE INFRAESTRUTURA

### Q1 2026: MVP (ATUAL)
```
✅ Single instance
✅ 15-20 câmeras
✅ 20-30 DAU
✅ R$ 500/mês infra
```

### Q2 2026: Multi-instância
```
🔄 3x MediaMTX instances
🔄 30-50 câmeras
🔄 50-80 DAU
🔄 R$ 1,500/mês infra
```

### Q3-Q4 2026: Docker Swarm
```
🔄 5-10 nodes
🔄 100-200 câmeras
🔄 150-300 DAU
🔄 R$ 5,000/mês infra
```

### 2027: Kubernetes
```
🔄 K8s cluster
🔄 500+ câmeras
🔄 500+ DAU
🔄 R$ 15,000/mês infra OU on-premise
```

---

## ✅ RECOMENDAÇÕES

### Curto Prazo (0-6 meses)
1. ✅ Manter arquitetura atual
2. ✅ Focar em vendas (até 8 clientes)
3. ✅ Monitorar métricas de uso
4. ✅ Preparar multi-instância

### Médio Prazo (6-12 meses)
1. 🔄 Implementar multi-instância
2. 🔄 Migrar storage para MinIO
3. 🔄 Load balancer (HAProxy)
4. 🔄 Monitoramento avançado

### Longo Prazo (12-24 meses)
1. 🔄 Avaliar Kubernetes vs On-premise
2. 🔄 CDN para HLS
3. 🔄 Auto-scaling
4. 🔄 Multi-região

---

## 📈 KPIs DE CAPACIDADE

### Monitorar Semanalmente
- CPU usage (alerta >70%)
- RAM usage (alerta >75%)
- Storage usage (alerta >80%)
- Viewers simultâneos (alerta >50)
- Drift events (alerta >10/hora)

### Monitorar Mensalmente
- DAU / MAU ratio
- Câmeras por cliente
- Tempo médio de visualização
- Taxa de crescimento MRR
- Custo por câmera

### Triggers de Upgrade
- CPU >80% por 7 dias
- RAM >85% por 3 dias
- Viewers >60 simultâneos
- Câmeras >25
- MRR >R$ 3,000/mês
