# Multi-Tenant + Planos - MÉTRICAS E CÁLCULOS

## 📊 Definições de Métricas

### DAU (Daily Active Users)
**Definição:** Usuários únicos que fazem login por dia

**Fórmula:**
```
DAU = Σ(unique_logins_per_day)
```

**Estimativa por Plano:**
```
Basic:   DAU = 3 usuários × 0.8 (taxa de uso) = 2.4 ≈ 2 DAU
Pro:     DAU = 5 usuários × 0.8 = 4 DAU
Premium: DAU = 10 usuários × 0.8 = 8 DAU
```

---

### RPS (Requests Per Second)
**Definição:** Requisições HTTP por segundo

**Fórmula:**
```
RPS = (DAU × requests_per_user_per_day) / 86400

Onde:
- requests_per_user_per_day = média de requisições por usuário
- 86400 = segundos em um dia
```

**Breakdown por Tipo de Requisição:**
```
1. Login: 1 req/dia
2. Camera List: 10 req/dia (refresh a cada 1h)
3. Stream Status: 60 req/dia (1 req/min durante 1h de uso)
4. Detections: 20 req/dia
5. Playback: 5 req/dia

Total: ~96 req/user/dia
```

**Cálculo por Plano:**
```
Basic (2 DAU):
RPS = (2 × 96) / 86400 = 0.0022 RPS

Pro (4 DAU):
RPS = (4 × 96) / 86400 = 0.0044 RPS

Premium (8 DAU):
RPS = (8 × 96) / 86400 = 0.0089 RPS
```

**RPS Total (100 organizações):**
```
Distribuição:
- 60% Basic: 60 × 0.0022 = 0.132 RPS
- 30% Pro: 30 × 0.0044 = 0.132 RPS
- 10% Premium: 10 × 0.0089 = 0.089 RPS

Total: 0.353 RPS ≈ 1 RPS (com margem de segurança)
```

---

### RPD (Requests Per Day)
**Definição:** Total de requisições por dia

**Fórmula:**
```
RPD = RPS × 86400
```

**Cálculo por Plano:**
```
Basic:   RPD = 0.0022 × 86400 = 190 req/dia
Pro:     RPD = 0.0044 × 86400 = 380 req/dia
Premium: RPD = 0.0089 × 86400 = 769 req/dia
```

**RPD Total (100 organizações):**
```
RPD = 0.353 × 86400 = 30,499 req/dia ≈ 31k req/dia
```

---

## 💾 Armazenamento de Gravações

### Fórmula de Armazenamento por Câmera

```
Storage_per_camera = bitrate × recording_hours × days / 8

Onde:
- bitrate = 2 Mbps (H.264 1080p)
- recording_hours = 24h/dia
- days = dias de retenção do plano
- /8 = conversão de bits para bytes
```

**Cálculo:**
```
Storage_per_camera_per_day = (2 Mbps × 24h × 3600s) / 8
                            = (2 × 24 × 3600) / 8 MB
                            = 172,800 / 8 MB
                            = 21,600 MB
                            = 21.6 GB/dia/câmera
```

### Armazenamento por Plano

**Basic (7 dias, 10 câmeras):**
```
Storage = 21.6 GB × 7 dias × 10 câmeras
        = 1,512 GB
        = 1.5 TB
```

**Pro (15 dias, 50 câmeras):**
```
Storage = 21.6 GB × 15 dias × 50 câmeras
        = 16,200 GB
        = 16.2 TB
```

**Premium (30 dias, 200 câmeras):**
```
Storage = 21.6 GB × 30 dias × 200 câmeras
        = 129,600 GB
        = 129.6 TB
```

---

## 💰 Custos de Infraestrutura

### Custo de Storage (AWS S3)

**Fórmula:**
```
Cost_storage = (total_GB / 1024) × price_per_TB_per_month

Onde:
- price_per_TB_per_month = $23 (S3 Standard)
```

**Por Plano:**
```
Basic:   Cost = (1,512 / 1024) × $23 = $34/mês
Pro:     Cost = (16,200 / 1024) × $23 = $364/mês
Premium: Cost = (129,600 / 1024) × $23 = $2,908/mês
```

---

### Custo de Compute (Backend)

**Fórmula:**
```
Cost_compute = (RPS / capacity_per_instance) × instance_cost

Onde:
- capacity_per_instance = 100 RPS (t3.medium)
- instance_cost = $30/mês
```

**Cálculo (100 organizações):**
```
Instances_needed = 1 RPS / 100 RPS = 0.01 ≈ 1 instância
Cost = 1 × $30 = $30/mês
```

---

### Custo de Banco de Dados

**Fórmula:**
```
Cost_db = (total_orgs / orgs_per_instance) × db_instance_cost

Onde:
- orgs_per_instance = 10 (PostgreSQL RDS t3.medium)
- db_instance_cost = $50/mês
```

**Cálculo (100 organizações):**
```
DB_instances = 100 / 10 = 10 instâncias
Cost = 10 × $50 = $500/mês
```

---

### Custo de Streaming (MediaMTX)

**Fórmula:**
```
Cost_streaming = (total_cameras / cameras_per_instance) × instance_cost

Onde:
- cameras_per_instance = 50 (t3.large)
- instance_cost = $60/mês
```

**Cálculo (100 organizações):**
```
Total_cameras = (60 × 10) + (30 × 50) + (10 × 200)
              = 600 + 1,500 + 2,000
              = 4,100 câmeras

Instances = 4,100 / 50 = 82 instâncias
Cost = 82 × $60 = $4,920/mês
```

---

## 📈 Custo Total por Cenário

### Cenário: 100 Organizações

**Distribuição:**
- 60 Basic
- 30 Pro
- 10 Premium

**Breakdown:**
```
Storage:
  - Basic: 60 × $34 = $2,040
  - Pro: 30 × $364 = $10,920
  - Premium: 10 × $2,908 = $29,080
  Total Storage: $42,040/mês

Compute: $30/mês
Database: $500/mês
Streaming: $4,920/mês

TOTAL: $47,490/mês
```

**Por Organização:**
```
Average = $47,490 / 100 = $474.90/org/mês
```

---

## 🎯 Pricing Sugerido

**Margem de Lucro: 3x custo**

```
Basic:
  Custo: $34 (storage) + $5 (infra) = $39
  Preço: $39 × 3 = $117/mês

Pro:
  Custo: $364 (storage) + $15 (infra) = $379
  Preço: $379 × 3 = $1,137/mês

Premium:
  Custo: $2,908 (storage) + $50 (infra) = $2,958
  Preço: $2,958 × 3 = $8,874/mês
```

---

## 📊 Métricas de Capacidade

### Limite de Organizações por Servidor

**Backend (t3.medium):**
```
Max_orgs = (100 RPS × 0.7 utilization) / 0.353 RPS
         = 70 / 0.353
         = 198 organizações
```

**Database (RDS t3.medium):**
```
Max_orgs = 10 organizações/instância
```

**Streaming (t3.large):**
```
Max_cameras = 50 câmeras/instância
Max_orgs = 50 / 41 (média de câmeras/org)
         = 1.2 organizações/instância
```

**Gargalo: Streaming**

---

## 🔢 Fórmulas de Referência

### Taxa de Crescimento
```
Growth_rate = (new_orgs - old_orgs) / old_orgs × 100%
```

### Churn Rate
```
Churn = (canceled_subs / total_subs) × 100%
```

### MRR (Monthly Recurring Revenue)
```
MRR = Σ(subscription_price × active_subscriptions)
```

### CAC (Customer Acquisition Cost)
```
CAC = total_marketing_spend / new_customers
```

### LTV (Lifetime Value)
```
LTV = ARPU × (1 / churn_rate)

Onde:
- ARPU = Average Revenue Per User
```
