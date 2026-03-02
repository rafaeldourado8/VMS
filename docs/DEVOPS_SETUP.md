# Setup DevOps Completo - VMS

## 🎯 Fluxo DevOps Implementado

```
Código Local → Git Push → GitHub Actions → Build → ECR → Deploy EC2 → Health Check
```

## ✅ Já Criado (Terraform)
- EC2: 34.232.245.164
- VPC + Security Groups
- S3 para backups
- IAM roles

## 🚀 Setup Passo a Passo

### 1. Configurar GitHub Secrets

**GitHub → Settings → Secrets and variables → Actions → New repository secret**

```bash
# AWS Credentials (configurar via GitHub Secrets)
AWS_ACCESS_KEY_ID=<SUA_ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<SUA_SECRET_KEY>

# Database
POSTGRES_DB=gtvision_db
POSTGRES_USER=gtvision_user
POSTGRES_PASSWORD=<SENHA_FORTE>

# Django
DJANGO_SECRET_KEY=<GERAR_CHAVE_50_CARACTERES>
ALLOWED_HOSTS=34.232.245.164,localhost

# API Token (para testes)
API_TOKEN=<TOKEN_SEGURO>
```

### 2. Conectar ao Servidor EC2

```bash
ssh -i vms-dev-key.pem ubuntu@34.232.245.164
```

### 3. Setup Inicial no Servidor

```bash
# Aguardar user-data terminar (Docker, AWS CLI, etc)
tail -f /var/log/cloud-init-output.log

# Clonar repositório
cd /home/ubuntu
git clone https://github.com/SEU_USUARIO/VMS.git
cd VMS

# Configurar GitHub Runner
# Obter token: GitHub → Settings → Actions → Runners → New self-hosted runner
bash scripts/setup_runner.sh <GITHUB_TOKEN>

# Verificar runner
sudo systemctl status actions.runner.*
```

### 4. Criar Branch Develop e Testar CI/CD

```bash
# No seu computador local (não no servidor)
cd D:\VMS

# Criar branch develop
git checkout -b develop

# Commit inicial
git add .
git commit -m "feat: setup CI/CD pipeline"

# Push para GitHub
git push origin develop
```

### 5. GitHub Actions Vai Executar Automaticamente

**Workflow: `.github/workflows/deploy-dev.yml`**

```
Job 1: test
  ✓ Setup Python
  ✓ Install dependencies
  ✓ Run migrations
  ✓ Run tests
  ✓ Lint code
  ✓ Build frontend

Job 2: build-and-push
  ✓ Login to ECR
  ✓ Build backend image
  ✓ Build frontend image
  ✓ Push to ECR

Job 3: deploy (self-hosted runner no EC2)
  ✓ Pull images from ECR
  ✓ Create .env file
  ✓ docker-compose up -d
  ✓ Run migrations
  ✓ Collect static files
  ✓ Health check
```

### 6. Verificar Deploy

```bash
# No servidor EC2
docker-compose ps

# Ver logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Testar endpoints
curl http://localhost/api/health/
curl http://localhost/
```

### 7. Acessar Aplicação

- **Frontend**: http://34.232.245.164
- **Backend API**: http://34.232.245.164/api
- **Admin Django**: http://34.232.245.164/admin
- **HAProxy Stats**: http://34.232.245.164:8404/stats

## 🔄 Fluxo de Desenvolvimento

### Fazer Mudanças

```bash
# Editar código localmente
code backend/apps/cameras/views.py

# Commit
git add .
git commit -m "feat: add new camera endpoint"

# Push
git push origin develop

# GitHub Actions vai:
# 1. Rodar testes
# 2. Build imagens
# 3. Deploy automático no EC2
```

### Monitorar Deploy

```bash
# Ver GitHub Actions
# https://github.com/SEU_USUARIO/VMS/actions

# Ver logs do runner no EC2
ssh -i vms-dev-key.pem ubuntu@34.232.245.164
sudo journalctl -u actions.runner.* -f
```

## 📊 Monitoramento

### Logs Centralizados

```bash
# Backend
docker-compose logs -f backend

# Frontend
docker-compose logs -f frontend

# Todos os serviços
docker-compose logs -f
```

### Health Checks

```bash
# API Health
curl http://34.232.245.164/api/health/

# Frontend
curl http://34.232.245.164/

# Database
docker-compose exec postgres_db psql -U gtvision_user -d gtvision_db -c "SELECT 1;"
```

### Métricas

- **CloudWatch**: CPU, Memory, Disk
- **HAProxy Stats**: http://34.232.245.164:8404/stats

## 🔧 Troubleshooting

### Deploy Falhou

```bash
# Ver logs do GitHub Actions
# GitHub → Actions → Deploy to Development → Ver job que falhou

# Conectar no servidor
ssh -i vms-dev-key.pem ubuntu@34.232.245.164

# Ver logs do runner
sudo journalctl -u actions.runner.* -n 100

# Ver logs dos containers
docker-compose logs --tail=100
```

### Rollback

```bash
# Reverter commit
git revert HEAD
git push origin develop

# Ou fazer deploy de commit específico
git checkout <commit-hash>
git push origin develop --force
```

### Reiniciar Serviços

```bash
# No servidor EC2
docker-compose restart backend
docker-compose restart frontend

# Ou reiniciar tudo
docker-compose down
docker-compose up -d
```

## 💾 Backup Automático

**Configurado via cron no servidor:**

```bash
# Backup diário às 2h AM
0 2 * * * /home/ubuntu/VMS/scripts/backup_db.sh >> /var/log/vms-backup.log 2>&1
```

**Backups vão para:**
- Local: `/home/ubuntu/backups/`
- S3: `s3://vms-dev-backups-239857123540/dev/`

**Retenção:**
- Local: 7 dias
- S3: 7 dias (configurado no Terraform)

## 💰 Gerenciar Custos

### Desligar Servidor (Economizar)

```bash
# Via Terraform
cd terraform/dev
terraform destroy -target=aws_instance.dev

# Via AWS CLI
aws ec2 stop-instances --instance-ids i-0e953f0681b7f3c67

# Via script
bash scripts/aws/stop-dev.sh
```

### Ligar Servidor

```bash
# Via AWS CLI
aws ec2 start-instances --instance-ids i-0e953f0681b7f3c67

# Via script
bash scripts/aws/start-dev.sh
```

**Custo:**
- Ligado: ~$0.13/hora = ~$95/mês
- Desligado: ~$8/mês (só EBS)
- **Economia**: Desligue 16h/dia = ~$43/mês

## 📈 Próximos Passos

1. ✅ Infraestrutura criada
2. ✅ CI/CD configurado
3. ⏳ Configurar secrets no GitHub
4. ⏳ Setup GitHub Runner no EC2
5. ⏳ Primeiro deploy via push
6. ⏳ Configurar notificações (Slack/Discord)
7. ⏳ Adicionar testes de carga no CI
8. ⏳ Configurar produção

## 🔗 Links Úteis

- **GitHub Actions**: https://github.com/SEU_USUARIO/VMS/actions
- **ECR Console**: https://console.aws.amazon.com/ecr/repositories
- **EC2 Console**: https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#Instances:instanceId=i-0e953f0681b7f3c67
- **S3 Backups**: https://s3.console.aws.amazon.com/s3/buckets/vms-dev-backups-239857123540
- **CloudWatch**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1

## 📞 Suporte

- Documentação: `docs/CI_CD_SETUP.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
- Architecture: `docs/ARCHITECTURE_CHANGES.md`
