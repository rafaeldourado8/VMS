# Implementação Rápida - Hoje

## ⏱️ Tempo Total: ~2 horas

---

## 1️⃣ Setup AWS (30 min)

### Instalar ferramentas

```bash
# AWS CLI
winget install Amazon.AWSCLI

# Terraform
winget install Hashicorp.Terraform

# Verificar
aws --version
terraform --version
```

### Configurar AWS

```bash
aws configure
# AWS Access Key ID: [SUA_KEY]
# AWS Secret Access Key: [SEU_SECRET]
# Default region: us-east-1
# Default output format: json
```

### Criar recursos base

```bash
# Bucket para Terraform state
aws s3 mb s3://vms-terraform-state --region us-east-1

# ECR repositories
aws ecr create-repository --repository-name vms/backend --region us-east-1
aws ecr create-repository --repository-name vms/frontend --region us-east-1
aws ecr create-repository --repository-name vms/lpr --region us-east-1
aws ecr create-repository --repository-name vms/recording --region us-east-1
aws ecr create-repository --repository-name vms/onvif --region us-east-1

# Anotar o registry URL
aws ecr describe-repositories --query 'repositories[0].repositoryUri' --output text
# Exemplo: 123456789012.dkr.ecr.us-east-1.amazonaws.com/vms/backend
```

---

## 2️⃣ Configurar GitHub Secrets (10 min)

Vá em: **GitHub → Settings → Secrets and variables → Actions → New repository secret**

Adicione:

```
AWS_ACCESS_KEY_ID = [sua access key]
AWS_SECRET_ACCESS_KEY = [seu secret key]
AWS_REGION = us-east-1
ECR_REGISTRY = [seu-account-id].dkr.ecr.us-east-1.amazonaws.com
```

---

## 3️⃣ Deploy Infraestrutura Dev (30 min)

```bash
cd d:\VMS\terraform\dev

# Inicializar
terraform init

# Planejar (revisar o que será criado)
terraform plan -out=tfplan

# Aplicar
terraform apply tfplan

# Anotar outputs importantes
terraform output alb_dns
terraform output ecs_cluster_name
```

**Recursos criados:**
- VPC com 2 subnets públicas
- RDS PostgreSQL t3.micro
- ElastiCache Redis t3.micro
- ECS Cluster (Fargate Spot)
- ALB
- Security Groups
- EventBridge rules (liga 7h, desliga 18h MS)

**Custo estimado:** ~$43/mês

---

## 4️⃣ Criar Task Definitions ECS (20 min)

```bash
# Criar arquivo de task definition
cd d:\VMS
```

Criar `ecs-task-def-dev.json`:

```json
{
  "family": "vms-dev-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "[ECR_REGISTRY]/vms/backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DEBUG", "value": "False"},
        {"name": "ALLOWED_HOSTS", "value": "*"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/vms-dev-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

Registrar task definition:

```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-def-dev.json
```

Criar serviço ECS:

```bash
aws ecs create-service \
  --cluster vms-dev-cluster \
  --service-name vms-dev-backend \
  --task-definition vms-dev-backend \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=backend,containerPort=8000"
```

---

## 5️⃣ Testar CI/CD (20 min)

```bash
# Commit e push
git add .
git commit -m "feat: Add AWS infrastructure and CI/CD"
git push origin main

# Criar branch dev
git checkout -b dev
git push origin dev

# Fazer uma mudança de teste
echo "# Test CI/CD" >> README.md
git add README.md
git commit -m "test: Trigger CI/CD pipeline"
git push origin dev
```

Acompanhar em: **GitHub → Actions**

Pipeline vai:
1. ✅ Rodar testes
2. ✅ Build Docker images
3. ✅ Push para ECR
4. ✅ Deploy no Dev
5. ✅ Rodar testes E2E

---

## 6️⃣ Validar Ambiente Dev (10 min)

```bash
# Pegar DNS do ALB
ALB_DNS=$(terraform output -raw alb_dns)

# Testar health check
curl http://$ALB_DNS/api/health/

# Ver logs
aws logs tail /ecs/vms-dev-backend --follow

# Ver status do serviço
aws ecs describe-services \
  --cluster vms-dev-cluster \
  --services vms-dev-backend
```

---

## 7️⃣ Deploy Produção (Opcional - 30 min)

**⚠️ ATENÇÃO: Produção custa ~$1,600/mês**

```bash
cd d:\VMS\terraform\prod

terraform init
terraform plan -out=tfplan

# REVISAR CUSTOS antes de aplicar!
terraform apply tfplan
```

---

## ✅ Checklist Final

- [ ] AWS CLI configurado
- [ ] Terraform instalado
- [ ] Bucket S3 criado
- [ ] ECR repositories criados
- [ ] GitHub Secrets configurados
- [ ] Infraestrutura Dev deployada
- [ ] Task definitions criadas
- [ ] Serviço ECS rodando
- [ ] CI/CD pipeline funcionando
- [ ] Health check passando
- [ ] Auto on/off configurado (7h-18h MS)

---

## 🔍 Verificar Auto On/Off

```bash
# Ver regras do EventBridge
aws events list-rules --name-prefix vms-dev

# Ver próximas execuções
aws events describe-rule --name vms-dev-start
aws events describe-rule --name vms-dev-stop

# Testar manualmente
aws lambda invoke \
  --function-name vms-dev-scheduler \
  --payload '{"action":"stop"}' \
  response.json

cat response.json
```

---

## 🆘 Troubleshooting

### Terraform init falha

```bash
# Verificar credenciais
aws sts get-caller-identity

# Verificar bucket existe
aws s3 ls s3://vms-terraform-state
```

### ECS task não inicia

```bash
# Ver eventos do serviço
aws ecs describe-services \
  --cluster vms-dev-cluster \
  --services vms-dev-backend \
  --query 'services[0].events[0:5]'

# Ver logs
aws logs tail /ecs/vms-dev-backend --follow
```

### Health check falha

```bash
# Testar diretamente
ALB_DNS=$(terraform output -raw alb_dns)
curl -v http://$ALB_DNS/api/health/

# Ver targets do ALB
aws elbv2 describe-target-health \
  --target-group-arn [ARN_DO_TARGET_GROUP]
```

---

## 📊 Monitorar Custos

```bash
# Ver custos do mês atual
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Criar alarme de custo
aws budgets create-budget \
  --account-id [SEU_ACCOUNT_ID] \
  --budget file://budget.json
```

Criar `budget.json`:

```json
{
  "BudgetName": "VMS-Dev-Monthly",
  "BudgetLimit": {
    "Amount": "50",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

---

## 🎯 Próximos Passos

1. ✅ Dev funcionando
2. ⏳ Testar por 1 semana
3. ⏳ Ajustar configurações
4. ⏳ Deploy Prod quando estável
5. ⏳ Migrar câmeras gradualmente
6. ⏳ Desligar ambiente local

---

## 📞 Suporte

- Documentação completa: `docs/AWS_DEV_PROD_SETUP.md`
- AWS Support: https://console.aws.amazon.com/support/
- Terraform Docs: https://registry.terraform.io/providers/hashicorp/aws/
