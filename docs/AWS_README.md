# AWS Dev/Prod - Documentação Completa

## 🚀 Start Aqui

**Objetivo**: Migrar desenvolvimento local para AWS com CI/CD automatizado

**Tempo**: ~2 horas para ambiente Dev funcionando

**Custo**: 
- Dev: $43/mês (liga 7h, desliga 18h MS)
- Prod: $1,601/mês (24/7, 500 câmeras)

---

## 📚 Documentação

### 1. Guia Principal
**[AWS_DEV_PROD_SETUP.md](AWS_DEV_PROD_SETUP.md)**
- Arquitetura completa
- Custos detalhados
- Setup passo a passo
- Troubleshooting

### 2. Quick Start (Implementar Hoje)
**[QUICK_START_AWS.md](QUICK_START_AWS.md)**
- ⏱️ 2 horas
- Comandos prontos
- Checklist
- Validação

### 3. Análise de Custos
**[AWS_COSTS.md](AWS_COSTS.md)**
- Breakdown detalhado
- Otimizações possíveis
- Cenários de crescimento
- ROI analysis

---

## ⚡ Implementação Rápida

### Opção 1: Script Automatizado (Recomendado)

```bash
cd d:\VMS
scripts\setup_aws_dev.bat
```

### Opção 2: Manual

```bash
# 1. Setup AWS
aws configure
aws s3 mb s3://vms-terraform-state --region us-east-1

# 2. Criar ECR
aws ecr create-repository --repository-name vms/backend --region us-east-1
aws ecr create-repository --repository-name vms/frontend --region us-east-1
aws ecr create-repository --repository-name vms/lpr --region us-east-1

# 3. Deploy infraestrutura
cd terraform/dev
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# 4. Configurar GitHub Secrets
# Vá em: Settings → Secrets → Actions
# Adicione: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ECR_REGISTRY

# 5. Push para GitHub
git add .
git commit -m "feat: Add AWS infrastructure"
git push origin dev
```

---

## 🏗️ Arquitetura

### Dev Environment
```
GitHub → Actions → ECR → ECS Fargate Spot
                         ↓
                    RDS t3.micro
                    Redis t3.micro
                    ALB
                         
Auto On:  7h MS (11h UTC)
Auto Off: 18h MS (22h UTC)
```

### Prod Environment
```
GitHub → Actions → ECR → ECS Fargate
                         ↓
                    RDS r5.2xlarge Multi-AZ
                    + 2 Read Replicas
                    Redis Cluster (Multi-AZ)
                    ALB + CloudFront
                    S3 (5TB recordings)
                    
Blue/Green Deployment
Auto Rollback on Failure
```

---

## 🔄 CI/CD Pipeline

```
Local Branch
    ↓ git push
GitHub Actions
    ├─ Unit Tests
    ├─ Integration Tests
    ├─ Build Docker
    └─ Push ECR
        ↓ PASSED
Deploy Dev
    ├─ ECS Update
    └─ E2E Tests
        ↓ PASSED
Merge → dev branch
    ↓ Manual Approval
Deploy Prod (Blue/Green)
    ├─ Deploy to Green
    ├─ Health Checks
    ├─ Switch Traffic
    └─ Rollback if Failed
        ↓ SUCCESS
Merge → main
```

---

## 📁 Arquivos Criados

```
VMS/
├── terraform/
│   ├── dev/
│   │   ├── main.tf              # Infraestrutura Dev
│   │   └── scheduler.py         # Lambda auto on/off
│   └── prod/
│       └── main.tf              # Infraestrutura Prod
├── .github/
│   └── workflows/
│       └── cicd.yml             # Pipeline CI/CD
├── scripts/
│   └── setup_aws_dev.bat        # Setup automatizado
├── docker-compose.test.yml      # Testes CI/CD
└── docs/
    ├── AWS_DEV_PROD_SETUP.md    # Guia completo
    ├── QUICK_START_AWS.md       # Quick start
    ├── AWS_COSTS.md             # Análise custos
    └── AWS_README.md            # Este arquivo
```

---

## ✅ Checklist de Implementação

### Hoje (Essencial)
- [ ] Instalar AWS CLI e Terraform
- [ ] Configurar credenciais AWS
- [ ] Criar bucket S3 e ECR repositories
- [ ] Configurar GitHub Secrets
- [ ] Deploy infraestrutura Dev
- [ ] Testar CI/CD pipeline
- [ ] Validar auto on/off

### Semana 1
- [ ] Monitorar custos Dev
- [ ] Ajustar configurações
- [ ] Criar alarmes CloudWatch
- [ ] Documentar runbooks
- [ ] Treinar equipe

### Semana 2
- [ ] Deploy infraestrutura Prod
- [ ] Configurar backup
- [ ] Testar disaster recovery
- [ ] Migrar 10 câmeras teste
- [ ] Validar performance

### Mês 1
- [ ] Migrar todas as câmeras
- [ ] Otimizar custos
- [ ] Implementar monitoring
- [ ] Desligar ambiente local
- [ ] Documentar lições aprendidas

---

## 💰 Custos Resumidos

### Dev (Desenvolvimento)
| Recurso | Custo/mês |
|---------|-----------|
| ECS Fargate Spot | $20 |
| RDS t3.micro | $6 |
| Redis t3.micro | $4 |
| ALB | $10 |
| Storage | $8 |
| **Total** | **$43** |

### Prod (500 Câmeras)
| Recurso | Custo/mês |
|---------|-----------|
| ECS Fargate | $496 |
| RDS Multi-AZ + Replicas | $2,332 |
| Redis Cluster | $274 |
| S3 (5TB) | $118 |
| CloudFront | $174 |
| Network | $138 |
| Backup | $50 |
| Monitoring | $65 |
| **Total** | **$1,601** |

**Com Reserved Instances: $658/mês (59% economia)**

---

## 🎯 Recursos AWS Criados

### Dev
- 1× VPC (10.0.0.0/16)
- 2× Subnets públicas
- 1× Internet Gateway
- 3× Security Groups
- 1× RDS PostgreSQL (db.t3.micro)
- 1× ElastiCache Redis (cache.t3.micro)
- 1× ECS Cluster (Fargate Spot)
- 1× Application Load Balancer
- 2× EventBridge Rules (on/off)
- 1× Lambda Function (scheduler)

### Prod
- 1× VPC (10.1.0.0/16)
- 2× Subnets públicas
- 1× Internet Gateway
- 3× Security Groups
- 1× RDS PostgreSQL Multi-AZ (db.r5.2xlarge)
- 2× RDS Read Replicas (db.r5.xlarge)
- 1× ElastiCache Redis Cluster (2 nodes)
- 1× ECS Cluster (Fargate)
- 1× Application Load Balancer
- 2× Target Groups (Blue/Green)
- 1× S3 Bucket (recordings)
- 1× CloudFront Distribution
- 10× CloudWatch Alarms

---

## 🆘 Troubleshooting Rápido

### Terraform falha
```bash
aws sts get-caller-identity  # Verificar credenciais
terraform init -reconfigure  # Reinicializar
```

### ECS task não inicia
```bash
aws ecs describe-services --cluster vms-dev-cluster --services vms-dev-backend
aws logs tail /ecs/vms-dev-backend --follow
```

### CI/CD falha
```bash
# Ver logs no GitHub Actions
# Verificar secrets configurados
# Testar build local: docker build -t test ./backend
```

### Custos altos
```bash
aws ce get-cost-and-usage --time-period Start=2025-01-01,End=2025-01-31 --granularity MONTHLY --metrics BlendedCost
```

---

## 📞 Suporte e Links

- **Documentação AWS**: https://docs.aws.amazon.com/
- **Terraform Registry**: https://registry.terraform.io/providers/hashicorp/aws/
- **GitHub Actions**: https://docs.github.com/en/actions
- **AWS Calculator**: https://calculator.aws
- **AWS Support**: https://console.aws.amazon.com/support/

---

## 🔐 Segurança

### Secrets no GitHub
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION
ECR_REGISTRY
```

### Secrets no AWS Secrets Manager
```
vms/dev/database
vms/dev/django
vms/prod/database
vms/prod/django
```

### IAM Roles
- ECS Task Execution Role
- ECS Task Role
- Lambda Scheduler Role
- CodeDeploy Role

---

## 📊 Monitoramento

### CloudWatch Dashboards
- CPU/Memory utilization
- Request count/latency
- Database connections
- Cache hit rate
- Error rate

### Alarmes Críticos
- CPU > 80%
- Memory > 85%
- Disk > 90%
- HTTP 5xx > 10/min
- Latency > 2s

---

## 🚀 Próximos Passos

1. ✅ Ler documentação completa
2. ⏳ Executar setup_aws_dev.bat
3. ⏳ Validar ambiente Dev
4. ⏳ Testar CI/CD
5. ⏳ Monitorar por 1 semana
6. ⏳ Deploy Prod
7. ⏳ Migrar câmeras
8. ⏳ Desligar local

**Boa sorte! 🎉**
