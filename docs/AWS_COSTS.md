# Análise de Custos AWS - VMS

## 💰 Resumo Executivo

| Ambiente | Custo Mensal | Custo Anual |
|----------|--------------|-------------|
| **Dev**  | $43          | $516        |
| **Prod** | $1,601       | $19,212     |
| **Total**| **$1,644**   | **$19,728** |

---

## 🔧 Ambiente Dev (Desenvolvimento)

### Compute
- **ECS Fargate Spot** (t3.large equivalent)
  - 2 vCPU, 8GB RAM
  - 11h/dia × 22 dias úteis = 242h/mês
  - $0.0832/hora × 242h = **$20.13/mês**

### Database
- **RDS PostgreSQL** (db.t3.micro)
  - 2 vCPU, 1GB RAM
  - Single-AZ
  - 20GB storage GP3
  - $0.017/hora × 242h = $4.11
  - Storage: $0.115/GB × 20GB = $2.30
  - **Total: $6.41/mês**

### Cache
- **ElastiCache Redis** (cache.t3.micro)
  - 2 vCPU, 0.5GB RAM
  - $0.017/hora × 242h = **$4.11/mês**

### Network
- **Application Load Balancer**
  - $0.0225/hora × 242h = $5.45
  - LCU: ~$5/mês
  - **Total: $10.45/mês**

### Storage
- **EBS** (100GB GP3)
  - $0.08/GB-month × 100GB = **$8.00/mês**

### Outros
- **CloudWatch Logs**: ~$2/mês
- **Data Transfer**: ~$2/mês

**Total Dev: $43/mês**

---

## 🏭 Ambiente Prod (Produção - 500 Câmeras)

### Compute
- **ECS Fargate** (c5.4xlarge equivalent)
  - 16 vCPU, 32GB RAM
  - 24/7 = 730h/mês
  - $0.68/hora × 730h = **$496.40/mês**

### Database
- **RDS PostgreSQL Primary** (db.r5.2xlarge)
  - 8 vCPU, 64GB RAM
  - Multi-AZ
  - 500GB storage GP3 (12,000 IOPS)
  - Instance: $0.96/hora × 730h × 2 (Multi-AZ) = $1,401.60
  - Storage: $0.115/GB × 500GB × 2 = $115.00
  - IOPS: $0.20/IOPS × 12,000 = $2,400 (included in GP3)
  - **Total Primary: $1,516.60/mês**

- **RDS Read Replica 1** (db.r5.xlarge)
  - 4 vCPU, 32GB RAM
  - $0.48/hora × 730h = $350.40
  - Storage: $0.115/GB × 500GB = $57.50
  - **Total Replica 1: $407.90/mês**

- **RDS Read Replica 2** (db.r5.xlarge)
  - 4 vCPU, 32GB RAM
  - **Total Replica 2: $407.90/mês**

**Total Database: $2,332.40/mês**

### Cache
- **ElastiCache Redis Cluster** (cache.r5.large)
  - 2 nodes (Multi-AZ)
  - 2 vCPU, 13.5GB RAM per node
  - $0.188/hora × 730h × 2 = **$274.48/mês**

### Storage (Gravações)
- **S3 Standard** (5TB = 5,120GB)
  - Primeiros 50TB: $0.023/GB
  - 5,120GB × $0.023 = **$117.76/mês**

- **S3 Lifecycle**
  - Após 30 dias → Standard-IA: $0.0125/GB
  - Após 90 dias → Glacier: $0.004/GB
  - Economia: ~40% após 90 dias

### CDN
- **CloudFront** (Distribuição de vídeos)
  - 2TB transfer/mês
  - $0.085/GB × 2,048GB = **$174.08/mês**

### Network
- **Application Load Balancer**
  - $0.0225/hora × 730h = $16.43
  - LCU: ~$30/mês (high traffic)
  - **Total: $46.43/mês**

- **Data Transfer Out**
  - 1TB/mês × $0.09/GB = **$92.16/mês**

### Backup
- **AWS Backup**
  - 500GB snapshots × $0.05/GB = $25.00
  - Restore: ~$25/mês (estimado)
  - **Total: $50.00/mês**

### Monitoring
- **CloudWatch**
  - Logs: 100GB × $0.50/GB = $50.00
  - Metrics: ~$10/mês
  - Alarms: 50 × $0.10 = $5.00
  - **Total: $65.00/mês**

### Outros
- **Secrets Manager**: $2.00/mês
- **Systems Manager**: $5.00/mês
- **Lambda** (scheduler, automation): $3.00/mês

**Total Prod: $1,601/mês**

---

## 📊 Breakdown por Categoria

### Dev
```
Compute:    $20  (47%)
Database:   $6   (14%)
Cache:      $4   (9%)
Network:    $10  (23%)
Storage:    $8   (19%)
Outros:     $4   (9%)
```

### Prod
```
Database:   $2,332  (46%)
Compute:    $496    (31%)
Cache:      $274    (17%)
Storage:    $118    (7%)
CDN:        $174    (11%)
Network:    $138    (9%)
Backup:     $50     (3%)
Monitoring: $65     (4%)
Outros:     $10     (1%)
```

---

## 💡 Otimizações Possíveis

### Dev (Economia: ~$15/mês)
1. **Usar Spot Instances**: Já implementado ✅
2. **Auto on/off**: Já implementado ✅
3. **Reduzir retention logs**: 3 dias → 1 dia (-$1/mês)
4. **Usar t4g (ARM)**: -20% custo (-$4/mês)

### Prod (Economia: ~$400/mês)
1. **Reserved Instances** (1 ano)
   - RDS: -30% = -$700/mês
   - ElastiCache: -30% = -$82/mês
   - **Economia: $782/mês**

2. **Savings Plans** (1 ano)
   - ECS Fargate: -20% = -$99/mês

3. **S3 Intelligent-Tiering**
   - Auto move para IA/Glacier
   - Economia: ~15% = -$18/mês

4. **CloudFront Reserved Capacity**
   - Economia: ~25% = -$44/mês

**Total Economia Possível: ~$943/mês (59%)**

**Custo Otimizado: $658/mês**

---

## 🎯 Cenários de Crescimento

### 1,000 Câmeras
- Compute: $992/mês (2x)
- Database: $3,500/mês (1.5x)
- Storage: $235/mês (2x)
- **Total: ~$2,800/mês**

### 2,000 Câmeras
- Compute: $1,984/mês (4x)
- Database: $5,000/mês (2x)
- Storage: $470/mês (4x)
- **Total: ~$4,500/mês**

### 5,000 Câmeras
- Compute: $4,960/mês (10x)
- Database: $8,000/mês (3x)
- Storage: $1,175/mês (10x)
- **Total: ~$9,500/mês**

---

## 📈 ROI Analysis

### Custo Local vs AWS (500 câmeras)

**Local (On-Premise)**
- Servidor: $15,000 (inicial)
- Manutenção: $500/mês
- Energia: $200/mês
- Internet: $300/mês
- **Total: $1,000/mês + $15k inicial**

**AWS**
- Sem custo inicial
- **Total: $1,601/mês**

**Break-even: 25 meses**

### Vantagens AWS
- ✅ Zero downtime
- ✅ Auto-scaling
- ✅ Backup automático
- ✅ Disaster recovery
- ✅ Global CDN
- ✅ Sem manutenção hardware
- ✅ Pay-as-you-grow

---

## 🔍 Monitoramento de Custos

### Alertas Recomendados

```bash
# Alerta se custo > $50/mês (Dev)
aws budgets create-budget --budget file://budget-dev.json

# Alerta se custo > $1,800/mês (Prod)
aws budgets create-budget --budget file://budget-prod.json

# Alerta diário de custos
aws ce get-cost-and-usage \
  --time-period Start=$(date -d "yesterday" +%Y-%m-%d),End=$(date +%Y-%m-%d) \
  --granularity DAILY \
  --metrics BlendedCost
```

### Cost Explorer Tags

Adicionar tags para rastreamento:
- `Environment`: dev/prod
- `Service`: backend/lpr/recording
- `CostCenter`: engineering
- `Project`: VMS

---

## 📞 Suporte

- AWS Cost Calculator: https://calculator.aws
- AWS Cost Explorer: https://console.aws.amazon.com/cost-management/
- AWS Trusted Advisor: https://console.aws.amazon.com/trustedadvisor/
