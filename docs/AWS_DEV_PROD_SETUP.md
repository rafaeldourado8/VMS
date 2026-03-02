# AWS Dev/Prod Setup - VMS

## 🎯 Objetivo

Migrar desenvolvimento local para AWS com:
- **Dev Server**: Barato, liga 7h e desliga 18h (horário MS)
- **Prod Server**: Robusto para 500 câmeras com gravações, backup e rollback
- **CI/CD**: Pipeline automatizado com testes e rollback

## 📋 Índice

1. [Arquitetura](#arquitetura)
2. [Custos Estimados](#custos-estimados)
3. [Setup Inicial](#setup-inicial)
4. [Ambiente Dev](#ambiente-dev)
5. [Ambiente Prod](#ambiente-prod)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Implementação Hoje](#implementação-hoje)

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                         DEVELOPER                            │
│                    git push → GitHub                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS                            │
│  1. Testes unitários                                         │
│  2. Testes integração                                        │
│  3. Build Docker images                                      │
│  4. Push para ECR                                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
┌──────────────────┐         ┌──────────────────┐
│   DEV SERVER     │         │   PROD SERVER    │
│   (t3.large)     │         │   (c5.4xlarge)   │
│   Auto On/Off    │         │   24/7 HA        │
│   7h-18h MS      │         │   500 cameras    │
└──────────────────┘         └──────────────────┘
```

---

## 💰 Custos Estimados

### Dev Server (t3.large - 2 vCPU, 8GB RAM)
- **Instância**: $0.0832/hora × 11h/dia × 22 dias = ~$20/mês
- **EBS**: 100GB GP3 = $8/mês
- **RDS**: db.t3.micro (dev) = $15/mês
- **Total Dev**: ~$43/mês

### Prod Server (c5.4xlarge - 16 vCPU, 32GB RAM)
- **Instância**: $0.68/hora × 730h = ~$496/mês
- **EBS**: 500GB GP3 = $40/mês
- **RDS**: db.r5.2xlarge Multi-AZ = ~$730/mês
- **S3**: 5TB gravações = ~$115/mês
- **CloudFront**: 2TB transfer = ~$170/mês
- **Backup**: AWS Backup = ~$50/mês
- **Total Prod**: ~$1,601/mês

**Total Geral**: ~$1,644/mês

---

## 🚀 Setup Inicial

### 1. Pré-requisitos

```bash
# Instalar AWS CLI
winget install Amazon.AWSCLI

# Configurar credenciais
aws configure
# AWS Access Key ID: <sua-key>
# AWS Secret Access Key: <seu-secret>
# Default region: us-east-1
# Default output format: json

# Instalar Terraform
winget install Hashicorp.Terraform

# Verificar instalação
aws sts get-caller-identity
terraform --version
```

### 2. Criar Estrutura de Arquivos

```bash
cd d:\VMS
mkdir -p terraform\{dev,prod,modules}
mkdir -p .github\workflows
```

---

## 🔧 Ambiente Dev

### Características
- Liga automaticamente às 7h (horário MS = UTC-4)
- Desliga automaticamente às 18h
- Usa Spot Instances para economia
- Banco de dados RDS t3.micro
- Sem backup automático (apenas snapshots manuais)

### Configuração

Ver arquivo: `terraform/dev/main.tf`

---

## 🏭 Ambiente Prod

### Características
- 24/7 disponibilidade
- Auto Scaling para 500 câmeras
- RDS Multi-AZ com réplicas de leitura
- S3 para gravações com lifecycle
- CloudFront para distribuição
- Backup automático diário
- Rollback automático em falhas

### Configuração

Ver arquivo: `terraform/prod/main.tf`

---

## 🔄 CI/CD Pipeline

### Fluxo Completo

```
Local Branch
    ↓ git push
GitHub Actions
    ↓ testes unitários
    ↓ testes integração
    ↓ build docker
    ↓ push ECR
    ↓ PASSED?
    ↓ YES
Deploy Dev
    ↓ testes E2E
    ↓ PASSED?
    ↓ YES
Merge → branch dev
    ↓ aprovação manual
    ↓ APPROVED?
    ↓ YES
Deploy Prod (Blue/Green)
    ↓ health checks
    ↓ PASSED?
    ↓ YES → Switch traffic
    ↓ NO → Rollback automático
Merge → main
```

### Arquivos do Pipeline

Ver: `.github/workflows/`

---

## ⚡ Implementação Hoje

### Passo 1: Setup AWS (30 min)

```bash
# 1. Criar bucket S3 para Terraform state
aws s3 mb s3://vms-terraform-state --region us-east-1

# 2. Criar ECR repositories
aws ecr create-repository --repository-name vms/backend --region us-east-1
aws ecr create-repository --repository-name vms/frontend --region us-east-1
aws ecr create-repository --repository-name vms/lpr --region us-east-1
aws ecr create-repository --repository-name vms/recording --region us-east-1
aws ecr create-repository --repository-name vms/onvif --region us-east-1

# 3. Criar secrets no GitHub
# Vá em: Settings → Secrets and variables → Actions
# Adicione:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - AWS_REGION (us-east-1)
# - ECR_REGISTRY (seu-account-id.dkr.ecr.us-east-1.amazonaws.com)
```

### Passo 2: Deploy Infraestrutura Dev (20 min)

```bash
cd terraform/dev

# Inicializar Terraform
terraform init

# Planejar mudanças
terraform plan -out=tfplan

# Aplicar (criar recursos)
terraform apply tfplan

# Anotar outputs
terraform output
```

### Passo 3: Configurar CI/CD (15 min)

```bash
# 1. Commit dos arquivos
git add .github/workflows/
git add terraform/
git commit -m "feat: Add AWS dev/prod infrastructure and CI/CD"

# 2. Push para GitHub
git push origin main

# 3. Criar branch dev
git checkout -b dev
git push origin dev

# 4. Configurar branch protection
# GitHub → Settings → Branches → Add rule
# - Branch name: main
# - Require pull request reviews
# - Require status checks to pass
```

### Passo 4: Primeiro Deploy (10 min)

```bash
# 1. Fazer uma mudança de teste
echo "# Test" >> README.md

# 2. Commit e push
git add README.md
git commit -m "test: Trigger CI/CD pipeline"
git push origin dev

# 3. Acompanhar no GitHub Actions
# GitHub → Actions → Ver workflow rodando

# 4. Se passar, fazer merge para main via PR
```

### Passo 5: Deploy Produção (30 min)

```bash
cd terraform/prod

# Inicializar
terraform init

# Planejar
terraform plan -out=tfplan

# Revisar custos
# IMPORTANTE: Produção é mais caro!

# Aplicar
terraform apply tfplan

# Configurar DNS (se tiver domínio)
# Apontar para o ALB do prod
```

---

## 📊 Monitoramento

### CloudWatch Dashboards

```bash
# Criar dashboard automático
aws cloudwatch put-dashboard \
  --dashboard-name VMS-Production \
  --dashboard-body file://cloudwatch-dashboard.json
```

### Alarmes Críticos

- CPU > 80% por 5 minutos
- Memória > 85%
- Disco > 90%
- Erros HTTP 5xx > 10/min
- Latência > 2s

---

## 🔐 Segurança

### Secrets Management

```bash
# Criar secrets no AWS Secrets Manager
aws secretsmanager create-secret \
  --name vms/prod/database \
  --secret-string '{"username":"admin","password":"CHANGE-ME"}'

aws secretsmanager create-secret \
  --name vms/prod/django \
  --secret-string '{"secret_key":"CHANGE-ME"}'
```

### Security Groups

- Dev: Acesso SSH apenas do seu IP
- Prod: Sem SSH, apenas Session Manager
- RDS: Apenas da VPC
- Redis: Apenas da VPC

---

## 🔄 Rollback

### Automático (CI/CD)

Se health checks falharem após deploy:
1. CloudWatch Alarm dispara
2. Lambda executa rollback
3. Reverte para versão anterior
4. Notifica no Slack/Email

### Manual

```bash
# Listar deployments
aws deploy list-deployments --application-name vms-prod

# Rollback para deployment anterior
aws deploy stop-deployment \
  --deployment-id d-XXXXXXXXX \
  --auto-rollback-enabled
```

---

## 📝 Checklist de Implementação

### Hoje (Essencial)
- [ ] Configurar AWS CLI
- [ ] Criar bucket S3 para Terraform
- [ ] Criar ECR repositories
- [ ] Configurar secrets no GitHub
- [ ] Deploy infraestrutura Dev
- [ ] Testar CI/CD pipeline
- [ ] Validar auto on/off do Dev

### Semana 1 (Importante)
- [ ] Deploy infraestrutura Prod
- [ ] Configurar monitoramento
- [ ] Configurar alarmes
- [ ] Testar rollback automático
- [ ] Documentar runbooks

### Semana 2 (Otimização)
- [ ] Configurar CloudFront
- [ ] Implementar WAF
- [ ] Otimizar custos
- [ ] Backup e restore
- [ ] Disaster recovery

---

## 🆘 Troubleshooting

### Dev não liga/desliga no horário

```bash
# Verificar EventBridge rules
aws events list-rules --name-prefix vms-dev

# Ver logs do Lambda
aws logs tail /aws/lambda/vms-dev-scheduler --follow
```

### Deploy falha no Prod

```bash
# Ver logs do CodeDeploy
aws deploy get-deployment --deployment-id d-XXXXXXXXX

# Ver logs da aplicação
aws logs tail /aws/ecs/vms-prod --follow
```

### Custos acima do esperado

```bash
# Ver custos por serviço
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

---

## 📚 Próximos Passos

1. Implementar hoje: Dev + CI/CD
2. Testar por 1 semana
3. Deploy Prod quando estável
4. Migrar câmeras gradualmente
5. Desligar ambiente local

---

## 🔗 Links Úteis

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Actions](https://docs.github.com/en/actions)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [AWS Cost Optimization](https://aws.amazon.com/pricing/cost-optimization/)
