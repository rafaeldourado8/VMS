# Checklist: Deploy VMS para Desenvolvimento

## Pré-requisitos
- [ ] Conta AWS configurada
- [ ] AWS CLI instalado e configurado
- [ ] Repositório GitHub criado
- [ ] Chave SSH gerada para EC2

## Fase 1: Criar Infraestrutura AWS (30 min)

### 1.1 Criar EC2 Spot Instance
```bash
cd scripts/aws
bash create-spot-instance.sh
```

- [ ] Instância criada
- [ ] IP público anotado: `___________________`
- [ ] Security Group configurado
- [ ] Chave SSH baixada e protegida

### 1.2 Conectar ao Servidor
```bash
chmod 400 vms-dev-key.pem
ssh -i vms-dev-key.pem ubuntu@SEU_IP
```

- [ ] Conexão SSH funcionando

## Fase 2: Configurar Servidor (20 min)

### 2.1 Setup Inicial
```bash
cd /home/ubuntu
git clone https://github.com/SEU_USUARIO/VMS.git
cd VMS
bash scripts/setup_ec2.sh
```

- [ ] Script executado
- [ ] Relogar no SSH

### 2.2 Configurar Ambiente
```bash
cd /home/ubuntu/VMS
cp .env.example .env
nano .env
```

Configurar:
- [ ] POSTGRES_PASSWORD
- [ ] DJANGO_SECRET_KEY
- [ ] DJANGO_ALLOWED_HOSTS (adicionar IP público)
- [ ] BACKEND_URL
- [ ] FRONTEND_URL

### 2.3 Iniciar Serviços
```bash
docker-compose up -d
docker-compose logs -f
```

- [ ] Todos os containers rodando
- [ ] Sem erros nos logs

### 2.4 Configurar Replicação PostgreSQL
```bash
bash scripts/init_postgres_replication.sh
```

- [ ] Replicação configurada
- [ ] Réplicas sincronizando

## Fase 3: GitHub Actions (30 min)

### 3.1 Configurar Self-Hosted Runner
```bash
cd /home/ubuntu/actions-runner
curl -o actions-runner-linux-x64-2.311.0.tar.gz -L \
  https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-linux-x64-2.311.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.311.0.tar.gz
```

No GitHub: Settings → Actions → Runners → New self-hosted runner
Copiar token e executar:

```bash
./config.sh --url https://github.com/SEU_USUARIO/VMS --token SEU_TOKEN
sudo ./svc.sh install
sudo ./svc.sh start
```

- [ ] Runner configurado
- [ ] Runner aparecendo como "Idle" no GitHub

### 3.2 Configurar Secrets no GitHub

GitHub → Settings → Secrets and variables → Actions

Adicionar:
- [ ] `DEV_POSTGRES_HOST` = postgres-primary
- [ ] `DEV_POSTGRES_DB` = vms_dev
- [ ] `DEV_POSTGRES_USER` = vms_user
- [ ] `DEV_POSTGRES_PASSWORD` = sua_senha
- [ ] `DEV_DJANGO_SECRET_KEY` = sua_chave
- [ ] `DEV_ALLOWED_HOSTS` = seu_ip,localhost
- [ ] `DEV_SERVER_IP` = seu_ip_publico

### 3.3 Testar CI/CD
```bash
git checkout -b develop
git add .
git commit -m "Initial setup"
git push origin develop
```

- [ ] Workflow executado
- [ ] Testes passaram
- [ ] Deploy realizado

## Fase 4: Validação (15 min)

### 4.1 Testar Endpoints
```bash
# No servidor
curl http://localhost/api/health/
curl http://localhost/
```

- [ ] API respondendo
- [ ] Frontend carregando

### 4.2 Testar Externamente
No navegador:
- [ ] `http://SEU_IP/` - Frontend
- [ ] `http://SEU_IP/api/` - API
- [ ] `http://SEU_IP/admin/` - Django Admin
- [ ] `http://SEU_IP:8404/stats` - HAProxy Stats

### 4.3 Testar RTSP
```bash
ffprobe rtsp://SEU_IP:8554/test
```

- [ ] MediaMTX respondendo

### 4.4 Verificar Logs
```bash
docker-compose logs --tail=50
```

- [ ] Sem erros críticos

## Fase 5: Configurar Backups (10 min)

### 5.1 Testar Backup Manual
```bash
bash scripts/backup_db.sh
ls -lh /home/ubuntu/backups/
```

- [ ] Backup criado
- [ ] Arquivo compactado

### 5.2 Verificar Cron
```bash
crontab -l
```

- [ ] Backup agendado para 2h AM

## Fase 6: Monitoramento (Opcional)

### 6.1 Configurar Alertas
- [ ] CloudWatch Alarm para CPU > 80%
- [ ] CloudWatch Alarm para Disk > 80%
- [ ] Status check alarm

### 6.2 Configurar Notificações
- [ ] Webhook Slack/Discord configurado
- [ ] Email de notificação configurado

## Informações Importantes

### URLs do Sistema
- Frontend: `http://SEU_IP/`
- Backend API: `http://SEU_IP/api/`
- Admin: `http://SEU_IP/admin/`
- HAProxy Stats: `http://SEU_IP:8404/stats`
- RTSP: `rtsp://SEU_IP:8554/`

### Credenciais
- Django Admin: criar com `docker-compose exec backend python manage.py createsuperuser`
- PostgreSQL: definido no .env
- HAProxy Stats: admin/admin (alterar em config/haproxy.cfg)

### Comandos Úteis
```bash
# Ver logs
docker-compose logs -f [service]

# Reiniciar serviço
docker-compose restart [service]

# Atualizar código
git pull && docker-compose up -d --build

# Backup manual
bash scripts/backup_db.sh

# Restaurar backup
bash scripts/restore_db.sh /home/ubuntu/backups/db_TIMESTAMP.sql.gz

# Ver status
docker-compose ps
htop
df -h
```

## Próximos Passos

- [ ] Configurar domínio (Route 53)
- [ ] Adicionar SSL/TLS (Let's Encrypt)
- [ ] Configurar monitoramento avançado
- [ ] Planejar migração para produção
- [ ] Documentar procedimentos operacionais
- [ ] Criar runbook de incidentes

## Custos Estimados

- EC2 t3.xlarge Spot: ~$22/mês
- EBS 100GB: ~$8/mês
- Transfer: ~$5/mês
- **Total: ~$35/mês**

## Suporte

- Documentação: `docs/AWS_EC2_SPOT_SETUP.md`
- Issues: GitHub Issues
- Logs: `/home/ubuntu/logs/`
