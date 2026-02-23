# Guia: EC2 Spot para Desenvolvimento com CI/CD

## Visão Geral

Este guia configura:
1. **EC2 Spot Instance** para servidor de desenvolvimento (economia de até 90%)
2. **GitHub Actions** para CI/CD automatizado
3. **Testes automatizados** antes do deploy
4. **Preparação para produção** com fallback e snapshots

---

## Fase 1: Criar EC2 Spot Instance

### 1.1 Configuração da Instância

**Especificações Recomendadas:**
- **Tipo**: t3.xlarge ou t3a.xlarge (4 vCPU, 16GB RAM)
- **OS**: Ubuntu 22.04 LTS
- **Storage**: 100GB gp3 (3000 IOPS)
- **Região**: us-east-1 (mais barato)

**Via AWS Console:**

1. Acesse EC2 → Launch Instance
2. Configure:
   ```
   Nome: vms-dev-spot
   AMI: Ubuntu Server 22.04 LTS
   Instance type: t3.xlarge
   
   ✅ Request Spot instances
   Maximum price: On-Demand price (deixe vazio para usar preço atual)
   Persistent request: ❌ (one-time)
   Interruption behavior: Stop (não Terminate)
   ```

3. **Key Pair**: Crie ou use existente (`vms-dev-key.pem`)

4. **Network Settings**:
   ```
   VPC: Default
   Auto-assign public IP: Enable
   
   Security Group: vms-dev-sg
   Inbound Rules:
   - SSH (22) - Seu IP
   - HTTP (80) - 0.0.0.0/0
   - HTTPS (443) - 0.0.0.0/0
   - Custom TCP (8554) - 0.0.0.0/0  # RTSP MediaMTX
   - Custom TCP (8404) - Seu IP      # HAProxy Stats
   ```

5. **Storage**: 100GB gp3

6. **Advanced Details**:
   ```bash
   # User data (script de inicialização)
   #!/bin/bash
   apt-get update
   apt-get install -y docker.io docker-compose git
   systemctl enable docker
   systemctl start docker
   usermod -aG docker ubuntu
   
   # Install GitHub Actions Runner dependencies
   apt-get install -y curl jq
   ```

### 1.2 Via AWS CLI (Alternativa)

```bash
# Criar Security Group
aws ec2 create-security-group \
  --group-name vms-dev-sg \
  --description "VMS Development Server"

# Adicionar regras
aws ec2 authorize-security-group-ingress \
  --group-name vms-dev-sg \
  --ip-permissions \
    IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges='[{CidrIp=SEU_IP/32}]' \
    IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges='[{CidrIp=0.0.0.0/0}]' \
    IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges='[{CidrIp=0.0.0.0/0}]' \
    IpProtocol=tcp,FromPort=8554,ToPort=8554,IpRanges='[{CidrIp=0.0.0.0/0}]'

# Criar Spot Instance Request
aws ec2 request-spot-instances \
  --spot-price "0.10" \
  --instance-count 1 \
  --type "one-time" \
  --launch-specification file://spot-config.json
```

**spot-config.json:**
```json
{
  "ImageId": "ami-0c7217cdde317cfec",
  "InstanceType": "t3.xlarge",
  "KeyName": "vms-dev-key",
  "SecurityGroups": ["vms-dev-sg"],
  "BlockDeviceMappings": [{
    "DeviceName": "/dev/sda1",
    "Ebs": {
      "VolumeSize": 100,
      "VolumeType": "gp3"
    }
  }],
  "UserData": "IyEvYmluL2Jhc2gKYXB0LWdldCB1cGRhdGUKYXB0LWdldCBpbnN0YWxsIC15IGRvY2tlci5pbyBkb2NrZXItY29tcG9zZSBnaXQ="
}
```

### 1.3 Elastic IP (Opcional mas Recomendado)

```bash
# Alocar IP fixo
aws ec2 allocate-address --domain vpc

# Associar à instância
aws ec2 associate-address \
  --instance-id i-1234567890abcdef0 \
  --allocation-id eipalloc-12345678
```

---

## Fase 2: Configurar Servidor

### 2.1 Conectar via SSH

```bash
chmod 400 vms-dev-key.pem
ssh -i vms-dev-key.pem ubuntu@SEU_IP_PUBLICO
```

### 2.2 Instalar Dependências

```bash
# Atualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Docker e Docker Compose
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Git e ferramentas
sudo apt-get install -y git curl jq make

# Relogar para aplicar grupo docker
exit
# Conectar novamente via SSH
```

### 2.3 Clonar Repositório

```bash
cd /home/ubuntu
git clone https://github.com/SEU_USUARIO/VMS.git
cd VMS
```

### 2.4 Configurar Ambiente

```bash
# Copiar .env de exemplo
cp .env.example .env

# Editar variáveis
nano .env
```

**Configurações importantes no .env:**
```bash
# Database
POSTGRES_HOST=postgres-primary
POSTGRES_DB=vms_dev
POSTGRES_USER=vms_user
POSTGRES_PASSWORD=SENHA_FORTE_AQUI

# Django
DJANGO_SECRET_KEY=GERAR_CHAVE_SEGURA
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=SEU_IP_PUBLICO,seu-dominio.com

# URLs públicas
BACKEND_URL=http://SEU_IP_PUBLICO/api
FRONTEND_URL=http://SEU_IP_PUBLICO
```

---

## Fase 3: GitHub Actions CI/CD

### 3.1 Criar Self-Hosted Runner

**No servidor EC2:**

```bash
# Criar diretório para runner
mkdir -p /home/ubuntu/actions-runner && cd /home/ubuntu/actions-runner

# Baixar runner (verificar versão mais recente no GitHub)
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz

# Extrair
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz

# Configurar (obter token no GitHub: Settings → Actions → Runners → New self-hosted runner)
./config.sh --url https://github.com/SEU_USUARIO/VMS --token SEU_TOKEN

# Instalar como serviço
sudo ./svc.sh install
sudo ./svc.sh start
```

### 3.2 Workflow de CI/CD

Criar `.github/workflows/deploy-dev.yml`:

```yaml
name: Deploy to Development

on:
  push:
    branches: [develop]
  pull_request:
    branches: [develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: vms_test
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run migrations
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/vms_test
        run: |
          cd backend
          python manage.py migrate
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/vms_test
        run: |
          cd backend
          python manage.py test
          
      - name: Lint Python
        run: |
          pip install flake8
          cd backend
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
      
      - name: Frontend tests
        run: |
          cd frontend
          npm ci
          npm run test -- --watchAll=false
          npm run build

  deploy:
    needs: test
    runs-on: self-hosted
    if: github.ref == 'refs/heads/develop' && github.event_name == 'push'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Create .env file
        run: |
          cat > .env << EOF
          POSTGRES_HOST=${{ secrets.POSTGRES_HOST }}
          POSTGRES_DB=${{ secrets.POSTGRES_DB }}
          POSTGRES_USER=${{ secrets.POSTGRES_USER }}
          POSTGRES_PASSWORD=${{ secrets.POSTGRES_PASSWORD }}
          DJANGO_SECRET_KEY=${{ secrets.DJANGO_SECRET_KEY }}
          DJANGO_DEBUG=False
          DJANGO_ALLOWED_HOSTS=${{ secrets.ALLOWED_HOSTS }}
          EOF
      
      - name: Stop services
        run: docker-compose down
      
      - name: Pull latest images
        run: docker-compose pull
      
      - name: Build and start services
        run: docker-compose up -d --build
      
      - name: Run migrations
        run: docker-compose exec -T backend python manage.py migrate
      
      - name: Collect static files
        run: docker-compose exec -T backend python manage.py collectstatic --noinput
      
      - name: Health check
        run: |
          sleep 10
          curl -f http://localhost/api/health || exit 1
      
      - name: Cleanup old images
        run: docker image prune -af

  notify:
    needs: [test, deploy]
    runs-on: ubuntu-latest
    if: always()
    
    steps:
      - name: Send notification
        run: |
          echo "Deploy status: ${{ needs.deploy.result }}"
          # Adicionar integração com Slack/Discord/Email aqui
```

### 3.3 Configurar Secrets no GitHub

**GitHub → Settings → Secrets and variables → Actions → New repository secret:**

```
POSTGRES_HOST=postgres-primary
POSTGRES_DB=vms_dev
POSTGRES_USER=vms_user
POSTGRES_PASSWORD=sua_senha_forte
DJANGO_SECRET_KEY=sua_chave_secreta
ALLOWED_HOSTS=seu-ip,seu-dominio.com
```

---

## Fase 4: Testes Automatizados

### 4.1 Estrutura de Testes

Criar `backend/tests/test_api.py`:

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User

class APITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')
    
    def test_health_endpoint(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
    
    def test_camera_list_requires_auth(self):
        response = self.client.get('/api/cameras/')
        self.assertEqual(response.status_code, 401)
    
    def test_camera_list_with_auth(self):
        self.client.login(username='test', password='pass')
        response = self.client.get('/api/cameras/')
        self.assertEqual(response.status_code, 200)
```

### 4.2 Testes de Integração

Criar `.github/workflows/integration-tests.yml`:

```yaml
name: Integration Tests

on:
  schedule:
    - cron: '0 */6 * * *'  # A cada 6 horas
  workflow_dispatch:

jobs:
  integration:
    runs-on: self-hosted
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run integration tests
        run: |
          cd tests
          python quick_test.py
      
      - name: Test RTSP streams
        run: |
          ffprobe -v error rtsp://localhost:8554/camera1 || exit 1
      
      - name: Test API endpoints
        run: |
          curl -f http://localhost/api/health || exit 1
          curl -f http://localhost/api/cameras/ || exit 1
      
      - name: Check database replication
        run: |
          docker-compose exec -T postgres-primary psql -U vms_user -d vms_dev -c "SELECT * FROM pg_stat_replication;"
```

---

## Fase 5: Preparação para Produção

### 5.1 Snapshots Automatizados

Criar script `scripts/backup_db.sh`:

```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/ubuntu/backups"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose exec -T postgres-primary pg_dump -U vms_user vms_dev | gzip > $BACKUP_DIR/db_$TIMESTAMP.sql.gz

# Upload para S3 (opcional)
aws s3 cp $BACKUP_DIR/db_$TIMESTAMP.sql.gz s3://vms-backups/dev/

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: db_$TIMESTAMP.sql.gz"
```

**Agendar com cron:**
```bash
crontab -e

# Adicionar linha:
0 2 * * * /home/ubuntu/VMS/scripts/backup_db.sh >> /var/log/vms-backup.log 2>&1
```

### 5.2 Snapshot de Volume EBS

```bash
# Via AWS CLI
aws ec2 create-snapshot \
  --volume-id vol-1234567890abcdef0 \
  --description "VMS Dev - $(date +%Y-%m-%d)" \
  --tag-specifications 'ResourceType=snapshot,Tags=[{Key=Name,Value=vms-dev-snapshot}]'
```

**Automatizar com Lambda (criar depois):**
- Snapshot diário às 3h AM
- Retenção: 7 dias para dev, 30 dias para prod

### 5.3 Monitoramento

Criar `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  prometheus-data:
  grafana-data:
```

---

## Fase 6: Estratégia de Produção

### 6.1 Arquitetura Futura

```
┌─────────────────────────────────────────────┐
│           Route 53 (DNS)                    │
│     vms.seudominio.com                      │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      Application Load Balancer              │
│   (Health checks + SSL termination)         │
└──────┬──────────────────────┬───────────────┘
       │                      │
       ▼                      ▼
┌─────────────┐        ┌─────────────┐
│  EC2 Prod   │        │  EC2 Prod   │
│  (Primary)  │◄──────►│  (Standby)  │
│  On-Demand  │        │  Spot/On-D  │
└──────┬──────┘        └──────┬──────┘
       │                      │
       └──────────┬───────────┘
                  ▼
         ┌────────────────┐
         │  RDS PostgreSQL│
         │  Multi-AZ      │
         │  + Read Replica│
         └────────────────┘
```

### 6.2 Checklist para Produção

**Infraestrutura:**
- [ ] Migrar para RDS PostgreSQL Multi-AZ
- [ ] Configurar Application Load Balancer
- [ ] Implementar Auto Scaling Group
- [ ] Configurar CloudWatch Alarms
- [ ] Implementar AWS Backup
- [ ] Configurar Route 53 com health checks
- [ ] SSL/TLS com ACM (AWS Certificate Manager)

**Segurança:**
- [ ] Secrets Manager para credenciais
- [ ] WAF (Web Application Firewall)
- [ ] Security Groups restritivos
- [ ] VPC com subnets privadas
- [ ] Bastion host para acesso SSH
- [ ] IAM roles com least privilege

**CI/CD:**
- [ ] Pipeline separado para produção
- [ ] Aprovação manual para deploy
- [ ] Blue-Green deployment
- [ ] Rollback automático em falhas
- [ ] Testes de carga antes do deploy

**Monitoramento:**
- [ ] CloudWatch Logs centralizados
- [ ] Alertas para erros críticos
- [ ] Dashboard de métricas
- [ ] APM (Application Performance Monitoring)
- [ ] Uptime monitoring externo

---

## Comandos Úteis

### Gerenciar Spot Instance

**💰 IMPORTANTE: Você pode desligar quando não estiver usando!**

Ver guia completo: [EC2_START_STOP.md](EC2_START_STOP.md)

```bash
# Ligar instância
bash scripts/aws/start-dev.sh

# Desligar instância (economizar ~$0.03/hora)
bash scripts/aws/stop-dev.sh

# Ver status
aws ec2 describe-instances --instance-ids i-1234567890abcdef0
```

**Economia:**
- 8h/dia útil: ~$13/mês (vs $30/mês 24/7)
- Você só paga quando está LIGADA!
- Dados persistem no EBS (não perde nada)

### Logs e Debug

```bash
# Logs do GitHub Actions Runner
sudo journalctl -u actions.runner.* -f

# Logs dos containers
docker-compose logs -f

# Logs específicos
docker-compose logs -f backend
docker-compose logs -f postgres-primary

# Status dos serviços
docker-compose ps
```

### Manutenção

```bash
# Limpar Docker
docker system prune -af --volumes

# Atualizar código
cd /home/ubuntu/VMS
git pull origin develop
docker-compose up -d --build

# Backup manual
./scripts/backup_db.sh

# Restaurar backup
gunzip < backup.sql.gz | docker-compose exec -T postgres-primary psql -U vms_user vms_dev
```

---

## Custos Estimados (us-east-1)

### Desenvolvimento (Spot)
- **EC2 t3.xlarge Spot**: ~$0.03/hora = ~$22/mês (24/7)
- **EBS 100GB gp3**: $8/mês
- **Elastic IP**: $0 (se associado)
- **Transfer**: ~$5/mês
- **Total**: ~$35/mês

### Produção (Estimativa)
- **EC2 t3.xlarge On-Demand x2**: ~$240/mês
- **RDS db.t3.large Multi-AZ**: ~$280/mês
- **ALB**: ~$25/mês
- **Backups e Snapshots**: ~$20/mês
- **Transfer e outros**: ~$50/mês
- **Total**: ~$615/mês

**Economia com Spot em Dev**: ~85% vs On-Demand

---

## Próximos Passos

1. **Agora**: Criar EC2 Spot e configurar CI/CD
2. **Semana 1**: Testes automatizados e monitoramento básico
3. **Semana 2**: Backups automatizados e documentação
4. **Semana 3**: Testes de carga e otimização
5. **Semana 4**: Planejar migração para produção

---

## Troubleshooting

### Spot Instance foi terminada
```bash
# Verificar histórico
aws ec2 describe-spot-instance-requests

# Criar nova request com mesmo volume EBS
# (se configurou para não deletar volume)
```

### GitHub Actions Runner offline
```bash
sudo systemctl status actions.runner.*
sudo systemctl restart actions.runner.*
```

### Deploy falhou
```bash
# Rollback para versão anterior
git log --oneline
git checkout <commit-anterior>
docker-compose up -d --build
```

### Banco de dados corrompido
```bash
# Restaurar último backup
./scripts/restore_db.sh backup_file.sql.gz
```

---

## Referências

- [AWS EC2 Spot Instances](https://aws.amazon.com/ec2/spot/)
- [GitHub Actions Self-hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Docker Compose Best Practices](https://docs.docker.com/compose/production/)
- [PostgreSQL Backup & Recovery](https://www.postgresql.org/docs/current/backup.html)
