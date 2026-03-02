# Tutorial Completo - Deploy AWS com CI/CD

## ⏱️ Tempo Total: 2-3 horas

---

## 📋 Pré-requisitos

- Conta AWS ativa
- Conta GitHub
- Git instalado
- Windows 10/11

---

## PARTE 1: Configurar AWS (40 min)

### Passo 1.1: Criar Conta IAM para Deploy (10 min)

1. **Acessar AWS Console**
   - Vá em: https://console.aws.amazon.com/
   - Login com sua conta

2. **Criar usuário IAM**
   ```
   AWS Console → IAM → Users → Add users
   
   User name: vms-deploy-user
   Access type: ☑ Programmatic access
   
   Click: Next: Permissions
   ```

3. **Adicionar permissões**
   ```
   ☑ Attach existing policies directly
   
   Selecione:
   - AmazonEC2ContainerRegistryFullAccess
   - AmazonECS_FullAccess
   - AmazonRDSFullAccess
   - AmazonElastiCacheFullAccess
   - AmazonS3FullAccess
   - AmazonVPCFullAccess
   - IAMFullAccess
   - CloudWatchLogsFullAccess
   - AWSCertificateManagerFullAccess
   
   Click: Next: Tags → Next: Review → Create user
   ```

4. **IMPORTANTE: Salvar credenciais**
   ```
   ⚠️ COPIE AGORA (não vai aparecer de novo):
   
   Access key ID: AKIAIOSFODNN7EXAMPLE
   Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   
   Salve em local seguro!
   ```

### Passo 1.2: Instalar AWS CLI (10 min)

1. **Baixar e instalar**
   ```bash
   # Abrir PowerShell como Administrador
   winget install Amazon.AWSCLI
   
   # Fechar e reabrir PowerShell
   aws --version
   # Deve mostrar: aws-cli/2.x.x
   ```

2. **Configurar credenciais**
   ```bash
   aws configure
   
   # Preencher:
   AWS Access Key ID [None]: AKIAIOSFODNN7EXAMPLE
   AWS Secret Access Key [None]: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   Default region name [None]: us-east-1
   Default output format [None]: json
   ```

3. **Testar conexão**
   ```bash
   aws sts get-caller-identity
   
   # Deve retornar:
   # {
   #     "UserId": "AIDAI...",
   #     "Account": "123456789012",
   #     "Arn": "arn:aws:iam::123456789012:user/vms-deploy-user"
   # }
   ```

### Passo 1.3: Criar Recursos Base AWS (20 min)

1. **Criar bucket S3 para Terraform**
   ```bash
   aws s3 mb s3://vms-terraform-state --region us-east-1
   
   # Habilitar versionamento
   aws s3api put-bucket-versioning \
     --bucket vms-terraform-state \
     --versioning-configuration Status=Enabled
   ```

2. **Criar ECR repositories**
   ```bash
   # Backend
   aws ecr create-repository \
     --repository-name vms/backend \
     --region us-east-1
   
   # Frontend
   aws ecr create-repository \
     --repository-name vms/frontend \
     --region us-east-1
   
   # LPR Service
   aws ecr create-repository \
     --repository-name vms/lpr \
     --region us-east-1
   
   # Recording Service
   aws ecr create-repository \
     --repository-name vms/recording \
     --region us-east-1
   
   # ONVIF Service
   aws ecr create-repository \
     --repository-name vms/onvif \
     --region us-east-1
   ```

3. **Anotar Account ID e Registry URL**
   ```bash
   # Pegar Account ID
   aws sts get-caller-identity --query Account --output text
   # Exemplo: 123456789012
   
   # Registry URL será:
   # 123456789012.dkr.ecr.us-east-1.amazonaws.com
   ```

---

## PARTE 2: Configurar GitHub (30 min)

### Passo 2.1: Criar Repositório GitHub (5 min)

1. **Criar novo repositório**
   ```
   GitHub → New repository
   
   Repository name: VMS
   Description: Video Management System
   ☑ Private
   ☐ Add README (já temos)
   
   Create repository
   ```

2. **Conectar repositório local**
   ```bash
   cd d:\VMS
   
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/VMS.git
   git push -u origin main
   ```

### Passo 2.2: Configurar GitHub Secrets (10 min)

1. **Acessar configurações**
   ```
   GitHub → Seu repositório VMS
   → Settings
   → Secrets and variables
   → Actions
   → New repository secret
   ```

2. **Adicionar secrets (um por vez)**

   **Secret 1: AWS_ACCESS_KEY_ID**
   ```
   Name: AWS_ACCESS_KEY_ID
   Secret: AKIAIOSFODNN7EXAMPLE
   
   Add secret
   ```

   **Secret 2: AWS_SECRET_ACCESS_KEY**
   ```
   Name: AWS_SECRET_ACCESS_KEY
   Secret: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   
   Add secret
   ```

   **Secret 3: AWS_REGION**
   ```
   Name: AWS_REGION
   Secret: us-east-1
   
   Add secret
   ```

   **Secret 4: ECR_REGISTRY**
   ```
   Name: ECR_REGISTRY
   Secret: 123456789012.dkr.ecr.us-east-1.amazonaws.com
   
   Add secret
   ```

3. **Verificar secrets criados**
   ```
   Você deve ver 4 secrets:
   ✓ AWS_ACCESS_KEY_ID
   ✓ AWS_SECRET_ACCESS_KEY
   ✓ AWS_REGION
   ✓ ECR_REGISTRY
   ```

### Passo 2.3: Configurar Branch Protection (5 min)

1. **Criar branch dev**
   ```bash
   cd d:\VMS
   git checkout -b dev
   git push origin dev
   ```

2. **Proteger branch main**
   ```
   GitHub → Settings → Branches → Add rule
   
   Branch name pattern: main
   
   ☑ Require a pull request before merging
   ☑ Require status checks to pass before merging
   ☑ Require branches to be up to date before merging
   
   Status checks:
   - test
   - build
   
   Create
   ```

### Passo 2.4: Configurar Environments (10 min)

1. **Criar environment de produção**
   ```
   GitHub → Settings → Environments → New environment
   
   Name: production
   
   Configure environment:
   ☑ Required reviewers
   Add: seu-usuario
   
   ☑ Wait timer: 0 minutes
   
   Save protection rules
   ```

---

## PARTE 3: Configurar SSH para EC2 (20 min)

### Passo 3.1: Gerar Par de Chaves SSH (5 min)

1. **Gerar chave SSH**
   ```bash
   # Abrir PowerShell
   cd ~\.ssh
   
   # Gerar chave
   ssh-keygen -t rsa -b 4096 -C "vms-deploy-key"
   
   # Quando perguntar:
   Enter file: vms-deploy-key
   Enter passphrase: [deixe vazio, apenas Enter]
   Enter same passphrase: [Enter novamente]
   
   # Criará 2 arquivos:
   # vms-deploy-key (privada)
   # vms-deploy-key.pub (pública)
   ```

2. **Ver chave pública**
   ```bash
   cat ~\.ssh\vms-deploy-key.pub
   
   # Copie o conteúdo (começa com ssh-rsa...)
   ```

### Passo 3.2: Importar Chave para AWS (5 min)

1. **Importar via AWS CLI**
   ```bash
   aws ec2 import-key-pair \
     --key-name vms-deploy-key \
     --public-key-material fileb://~/.ssh/vms-deploy-key.pub \
     --region us-east-1
   ```

2. **Verificar importação**
   ```bash
   aws ec2 describe-key-pairs --key-names vms-deploy-key
   ```

### Passo 3.3: Adicionar Chave Privada ao GitHub (10 min)

1. **Ler chave privada**
   ```bash
   cat ~\.ssh\vms-deploy-key
   
   # Copie TODO o conteúdo (incluindo BEGIN e END)
   ```

2. **Adicionar como secret**
   ```
   GitHub → Settings → Secrets and variables → Actions
   → New repository secret
   
   Name: EC2_SSH_PRIVATE_KEY
   Secret: [Cole o conteúdo da chave privada]
   
   Add secret
   ```

---

## PARTE 4: Instalar Terraform (10 min)

### Passo 4.1: Instalar Terraform

```bash
# PowerShell como Administrador
winget install Hashicorp.Terraform

# Fechar e reabrir PowerShell
terraform --version
# Deve mostrar: Terraform v1.x.x
```

### Passo 4.2: Inicializar Terraform

```bash
cd d:\VMS\terraform\dev

# Inicializar
terraform init

# Deve mostrar:
# Terraform has been successfully initialized!
```

---

## PARTE 5: Deploy Infraestrutura Dev (30 min)

### Passo 5.1: Criar Lambda para Scheduler (5 min)

```bash
cd d:\VMS\terraform\dev

# Criar ZIP do Lambda
powershell Compress-Archive -Path scheduler.py -DestinationPath scheduler.zip
```

### Passo 5.2: Planejar Deploy (5 min)

```bash
terraform plan -out=tfplan

# Revisar o que será criado:
# - VPC
# - Subnets
# - Security Groups
# - RDS PostgreSQL
# - ElastiCache Redis
# - ECS Cluster
# - ALB
# - EventBridge Rules
# - Lambda Function
```

### Passo 5.3: Aplicar Infraestrutura (15 min)

```bash
terraform apply tfplan

# Aguardar ~10-15 minutos
# Terraform criará todos os recursos

# Ao final, verá:
# Apply complete! Resources: XX added, 0 changed, 0 destroyed.
```

### Passo 5.4: Anotar Outputs (5 min)

```bash
terraform output

# Copie os valores:
alb_dns = "vms-dev-alb-123456.us-east-1.elb.amazonaws.com"
db_endpoint = "vms-dev-postgres.abc123.us-east-1.rds.amazonaws.com:5432"
redis_endpoint = "vms-dev-redis.abc123.cache.amazonaws.com"
ecs_cluster_name = "vms-dev-cluster"

# Salve esses valores!
```

---

## PARTE 6: Configurar Variáveis de Ambiente (15 min)

### Passo 6.1: Criar .env.dev

```bash
cd d:\VMS
cp .env.dev.example .env.dev
```

### Passo 6.2: Preencher com Outputs do Terraform

Editar `.env.dev`:

```bash
# Pegar do terraform output
DB_HOST=vms-dev-postgres.abc123.us-east-1.rds.amazonaws.com
REDIS_HOST=vms-dev-redis.abc123.cache.amazonaws.com
BASE_URL=http://vms-dev-alb-123456.us-east-1.elb.amazonaws.com

# Pegar senha do banco
terraform output -raw db_password
# Copiar e colar em:
POSTGRES_PASSWORD=senha_gerada_pelo_terraform
```

### Passo 6.3: Adicionar Secrets ao GitHub

```bash
# Pegar valores sensíveis
terraform output -raw db_password

# Adicionar no GitHub:
# Settings → Secrets → Actions → New secret
Name: DEV_DB_PASSWORD
Secret: [senha do terraform output]
```

---

## PARTE 7: Criar ECS Task Definition (20 min)

### Passo 7.1: Criar arquivo de task definition

```bash
cd d:\VMS
```

Criar `ecs-task-dev.json`:

```json
{
  "family": "vms-dev-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/vms/backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DEBUG", "value": "True"},
        {"name": "DB_HOST", "value": "vms-dev-postgres.abc123.us-east-1.rds.amazonaws.com"},
        {"name": "REDIS_HOST", "value": "vms-dev-redis.abc123.cache.amazonaws.com"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/vms-dev-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs",
          "awslogs-create-group": "true"
        }
      }
    }
  ]
}
```

### Passo 7.2: Criar IAM Role para ECS

```bash
# Criar role
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Anexar policy
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

### Passo 7.3: Registrar Task Definition

```bash
# Substituir Account ID no arquivo
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
(Get-Content ecs-task-dev.json) -replace '123456789012', $ACCOUNT_ID | Set-Content ecs-task-dev.json

# Registrar
aws ecs register-task-definition --cli-input-json file://ecs-task-dev.json
```

---

## PARTE 8: Testar CI/CD Pipeline (20 min)

### Passo 8.1: Fazer Commit de Teste

```bash
cd d:\VMS

# Criar branch de teste
git checkout dev

# Fazer mudança
echo "# CI/CD Test" >> README.md

# Commit e push
git add .
git commit -m "test: Trigger CI/CD pipeline"
git push origin dev
```

### Passo 8.2: Acompanhar Pipeline

```
1. Ir em: GitHub → Actions
2. Ver workflow "CI/CD Pipeline" rodando
3. Acompanhar cada step:
   ✓ Run Tests
   ✓ Build and Push Docker Images
   ✓ Deploy to Dev
```

### Passo 8.3: Verificar Deploy

```bash
# Pegar DNS do ALB
terraform output -raw alb_dns

# Testar (aguardar 2-3 minutos após deploy)
curl http://vms-dev-alb-123456.us-east-1.elb.amazonaws.com/api/health/

# Deve retornar: {"status": "ok"}
```

---

## PARTE 9: Validar Auto On/Off (10 min)

### Passo 9.1: Verificar EventBridge Rules

```bash
# Listar rules
aws events list-rules --name-prefix vms-dev

# Deve mostrar:
# - vms-dev-start (cron: 0 11 * * ? *)
# - vms-dev-stop (cron: 0 22 * * ? *)
```

### Passo 9.2: Testar Manualmente

```bash
# Desligar agora (teste)
aws lambda invoke \
  --function-name vms-dev-scheduler \
  --payload '{"action":"stop"}' \
  response.json

cat response.json

# Ligar novamente
aws lambda invoke \
  --function-name vms-dev-scheduler \
  --payload '{"action":"start"}' \
  response.json
```

---

## PARTE 10: Monitoramento (10 min)

### Passo 10.1: Ver Logs CloudWatch

```bash
# Logs do backend
aws logs tail /ecs/vms-dev-backend --follow

# Logs do Lambda scheduler
aws logs tail /aws/lambda/vms-dev-scheduler --follow
```

### Passo 10.2: Ver Métricas ECS

```
AWS Console → ECS → Clusters → vms-dev-cluster
→ Services → vms-dev-backend
→ Metrics
```

### Passo 10.3: Configurar Alarme de Custo

```bash
# Criar budget
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget '{
    "BudgetName": "VMS-Dev-Monthly",
    "BudgetLimit": {"Amount": "50", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST"
  }'
```

---

## ✅ Checklist Final

- [ ] AWS CLI instalado e configurado
- [ ] Terraform instalado
- [ ] Bucket S3 criado
- [ ] ECR repositories criados
- [ ] GitHub secrets configurados
- [ ] SSH keys geradas e importadas
- [ ] Infraestrutura Dev deployada
- [ ] Task definition registrada
- [ ] CI/CD pipeline funcionando
- [ ] Health check passando
- [ ] Auto on/off configurado
- [ ] Logs CloudWatch funcionando
- [ ] Alarme de custo configurado

---

## 🎯 Comandos Úteis

```bash
# Ver status do cluster
aws ecs describe-clusters --clusters vms-dev-cluster

# Ver serviços rodando
aws ecs list-services --cluster vms-dev-cluster

# Ver tasks rodando
aws ecs list-tasks --cluster vms-dev-cluster

# Ver logs em tempo real
aws logs tail /ecs/vms-dev-backend --follow

# Ver custos do mês
aws ce get-cost-and-usage \
  --time-period Start=2025-01-01,End=2025-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost

# Destruir tudo (se necessário)
cd terraform/dev
terraform destroy
```

---

## 🆘 Troubleshooting

### Erro: "Access Denied"
```bash
# Verificar credenciais
aws sts get-caller-identity

# Reconfigurar se necessário
aws configure
```

### Erro: "Bucket already exists"
```bash
# Bucket já existe, apenas continue
# Ou use nome diferente: vms-terraform-state-SEU-NOME
```

### Erro: "Task failed to start"
```bash
# Ver eventos do serviço
aws ecs describe-services \
  --cluster vms-dev-cluster \
  --services vms-dev-backend \
  --query 'services[0].events[0:5]'

# Ver logs
aws logs tail /ecs/vms-dev-backend --follow
```

### Pipeline falha no GitHub
```bash
# Verificar secrets configurados
GitHub → Settings → Secrets → Actions

# Deve ter:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - AWS_REGION
# - ECR_REGISTRY
```

---

## 📞 Próximos Passos

1. ✅ Dev funcionando
2. ⏳ Testar por 1 semana
3. ⏳ Deploy Prod (seguir mesmo processo)
4. ⏳ Configurar SSL/WAF (docs/SECURITY_SSL_SETUP.md)
5. ⏳ Migrar câmeras

**Parabéns! Ambiente Dev configurado! 🎉**
