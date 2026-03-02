# Guia Completo: CI/CD com GitHub Actions + EC2 Spot

## 📋 Pré-requisitos

✅ AWS CLI configurado (Account: 239857123540)
✅ Terraform instalado
✅ S3 bucket: `vms-terraform-state-gtvision`
✅ ECR repositories criados

## 🚀 Passo a Passo

### 1. Criar Key Pair SSH

```bash
# Windows (PowerShell)
aws ec2 create-key-pair --key-name vms-dev-key --query 'KeyMaterial' --output text | Out-File -Encoding ASCII vms-dev-key.pem

# Linux/Mac
aws ec2 create-key-pair --key-name vms-dev-key --query 'KeyMaterial' --output text > vms-dev-key.pem
chmod 400 vms-dev-key.pem
```

### 2. Configurar Terraform Dev

```bash
cd terraform/dev

# Editar terraform.tfvars
# Obter seu IP: curl ifconfig.me
notepad terraform.tfvars

# Inicializar e aplicar
terraform init
terraform plan
terraform apply
```

### 3. Conectar ao Servidor

```bash
# Obter IP público
terraform output public_ip

# Conectar via SSH
ssh -i vms-dev-key.pem ubuntu@<PUBLIC_IP>
```

### 4. Configurar Servidor (dentro do EC2)

```bash
# Clonar repositório
git clone https://github.com/SEU_USUARIO/VMS.git
cd VMS

# Configurar GitHub Runner
# Obter token: GitHub → Settings → Actions → Runners → New self-hosted runner
bash scripts/setup_runner.sh <GITHUB_TOKEN>

# Configurar .env
cp .env.example .env
nano .env
```

### 5. Configurar Secrets no GitHub

**GitHub → Settings → Secrets and variables → Actions → New repository secret:**

```
AWS_ACCESS_KEY_ID=<SUA_ACCESS_KEY>
AWS_SECRET_ACCESS_KEY=<SUA_SECRET_KEY>

POSTGRES_DB=gtvision_db
POSTGRES_USER=gtvision_user
POSTGRES_PASSWORD=<SENHA_FORTE>

DJANGO_SECRET_KEY=<GERAR_CHAVE>
ALLOWED_HOSTS=<PUBLIC_IP>,seu-dominio.com

API_TOKEN=<TOKEN_PARA_TESTES>
```

### 6. Testar CI/CD

```bash
# Criar branch develop
git checkout -b develop

# Fazer commit
git add .
git commit -m "Setup CI/CD"
git push origin develop

# GitHub Actions vai:
# 1. Rodar testes
# 2. Build imagens Docker
# 3. Push para ECR
# 4. Deploy no EC2
```

## 📊 Workflows Criados

### `.github/workflows/deploy-dev.yml`
- **Trigger**: Push/PR para `develop`
- **Jobs**:
  1. `test` - Testes unitários e lint
  2. `build-and-push` - Build e push para ECR
  3. `deploy` - Deploy no EC2 self-hosted runner
  4. `notify` - Notificação de status

### `.github/workflows/integration-tests.yml`
- **Trigger**: A cada 6 horas + manual
- **Jobs**: Testes de integração e health checks

## 🔧 Scripts Criados

### Backup/Restore
- `scripts/backup_db.sh` - Backup automático para S3
- `scripts/restore_db.sh` - Restore do backup

### AWS Management
- `scripts/aws/start-dev.sh` - Iniciar EC2
- `scripts/aws/stop-dev.sh` - Parar EC2 (economizar)
- `scripts/aws/start-dev.bat` - Windows version
- `scripts/aws/stop-dev.bat` - Windows version

### Setup
- `scripts/setup_runner.sh` - Configurar GitHub Runner

## 💰 Economia

### Desligar quando não usar:
```bash
# Windows
scripts\aws\stop-dev.bat

# Linux/Mac
bash scripts/aws/start-dev.sh
```

**Economia:**
- 8h/dia útil: ~$13/mês (vs $30/mês 24/7)
- 16h desligado/dia = ~$15/mês economizado

## 🔄 Fluxo de Deploy

```
1. Developer push para develop
   ↓
2. GitHub Actions: Run tests
   ↓
3. Tests pass → Build Docker images
   ↓
4. Push images to ECR
   ↓
5. Self-hosted runner on EC2 pulls images
   ↓
6. Deploy with docker-compose
   ↓
7. Run migrations
   ↓
8. Health check
   ↓
9. ✅ Deploy complete
```

## 📦 Docker Compose Prod

Arquivo `docker-compose.prod.yml` usa imagens do ECR:
- Backend: `239857123540.dkr.ecr.us-east-1.amazonaws.com/vms/backend`
- Frontend: `239857123540.dkr.ecr.us-east-1.amazonaws.com/vms/frontend`

## 🔍 Monitoramento

### Ver logs do runner:
```bash
sudo journalctl -u actions.runner.* -f
```

### Ver logs dos containers:
```bash
docker-compose logs -f
```

### Health checks:
```bash
curl http://localhost/api/health/
curl http://localhost/
```

## 🚨 Troubleshooting

### Runner offline:
```bash
sudo systemctl status actions.runner.*
sudo systemctl restart actions.runner.*
```

### Deploy falhou:
```bash
# Ver logs
docker-compose logs backend

# Rollback
git revert HEAD
git push origin develop
```

### Backup/Restore:
```bash
# Backup manual
bash scripts/backup_db.sh

# Restore
bash scripts/restore_db.sh backups/db_20260302_120000.sql.gz
```

## 📈 Próximos Passos

1. ✅ CI/CD configurado
2. ⏳ Configurar notificações (Slack/Discord)
3. ⏳ Adicionar testes de carga no CI
4. ⏳ Blue-Green deployment
5. ⏳ Monitoramento com CloudWatch

## 🔗 Links Úteis

- ECR Console: https://console.aws.amazon.com/ecr/repositories
- GitHub Actions: https://github.com/SEU_USUARIO/VMS/actions
- S3 Backups: https://s3.console.aws.amazon.com/s3/buckets/vms-dev-backups-239857123540
