# 💰 DVR-Lite - Custos AWS

Estimativa de custos mensais para deploy na AWS.

---

## 📊 Cenário Base: 20 Câmeras

### Compute (EC2)
**t3.large** (2 vCPU, 8GB RAM)
- On-Demand: $0.0832/hora
- Mensal: $60.74/mês
- Uso: Backend + MediaMTX + Recording

### Storage (S3)
**Gravações (7 dias)**
- 20 câmeras × 2 Mbps × 7 dias = 2.4 TB
- S3 Standard: $0.023/GB = $55.20/mês

**Clipes Permanentes**
- Estimativa: 100 GB/mês
- S3 Standard: $2.30/mês

**Total Storage: $57.50/mês**

### Database (RDS)
**db.t3.small** (2 vCPU, 2GB RAM)
- PostgreSQL: $0.034/hora
- Mensal: $24.82/mês
- Storage: 20GB × $0.115 = $2.30/mês
- **Total: $27.12/mês**

### Cache (ElastiCache)
**cache.t3.micro** (2 vCPU, 0.5GB RAM)
- Redis: $0.017/hora
- Mensal: $12.41/mês

### Load Balancer (ALB)
- ALB: $0.0225/hora = $16.43/mês
- LCU: ~$5/mês
- **Total: $21.43/mês**

### Data Transfer
**Streaming Out**
- 20 câmeras × 2 Mbps × 30 dias × 8h/dia = 1.44 TB
- Primeiros 10TB: $0.09/GB = $129.60/mês

**Playback Out**
- Estimativa: 500 GB/mês
- $0.09/GB = $45/mês

**Total Transfer: $174.60/mês**

---

## 💵 Total Mensal

| Serviço | Custo |
|---------|-------|
| EC2 (t3.large) | $60.74 |
| S3 Storage | $57.50 |
| RDS PostgreSQL | $27.12 |
| ElastiCache Redis | $12.41 |
| ALB | $21.43 |
| Data Transfer | $174.60 |
| **TOTAL** | **$353.80/mês** |

---

## 📉 Otimizações

### Usar Reserved Instances (1 ano)
- EC2: $60.74 → $38/mês (-37%)
- RDS: $27.12 → $17/mês (-37%)
- **Economia: $32.86/mês**

### Usar S3 Intelligent-Tiering
- Gravações antigas: $55.20 → $35/mês (-37%)
- **Economia: $20.20/mês**

### Usar CloudFront
- Cache de streaming: $174.60 → $100/mês (-43%)
- **Economia: $74.60/mês**

### Total com Otimizações
**$226.14/mês** (36% economia)

---

## 🎯 Custo por Câmera

- **Sem otimização:** $17.69/câmera/mês
- **Com otimização:** $11.31/câmera/mês

---

## 📈 Escalabilidade

### 10 Câmeras
- Storage: $28.75/mês
- Transfer: $87.30/mês
- **Total: ~$200/mês**

### 50 Câmeras
- Compute: t3.xlarge ($121/mês)
- Storage: $143.75/mês
- Transfer: $436.50/mês
- **Total: ~$750/mês**

### 100 Câmeras
- Compute: 2× t3.xlarge ($242/mês)
- Storage: $287.50/mês
- Transfer: $873/mês
- **Total: ~$1,450/mês**
