# 🔧 Troubleshooting - GTVision

## Problemas Identificados e Soluções

### ❌ Problema 1: RabbitMQ - Credenciais Inválidas

**Erro:**
```
ACCESS_REFUSED - Login was refused using authentication mechanism PLAIN
PLAIN login refused: user 'gtvision_user' - invalid credentials
```

**Causa:**
Inconsistência nas variáveis de ambiente entre `.env` e `docker-compose.yml`:
- `.env` define: `RABBITMQ_USER` e `RABBITMQ_PASS`
- `docker-compose.yml` espera: `RABBITMQ_DEFAULT_USER` e `RABBITMQ_DEFAULT_PASS`

**Solução:**
Adicionadas as variáveis corretas no `.env`:
```bash
RABBITMQ_DEFAULT_USER=gtvision_user
RABBITMQ_DEFAULT_PASS=your-rabbitmq-password-here
```

### ❌ Problema 2: HAProxy - Backend Indisponível

**Erro:**
```
backend api_gateway has no server available!
```

**Causa:**
O HAProxy está tentando acessar um backend `api_gateway` que não existe na configuração atual.

**Solução:**
A configuração do HAProxy usa `kong_gateway` como backend. Certifique-se de que:
1. Kong está rodando e saudável
2. Gateway (FastAPI) está rodando
3. Backend (Django) está saudável

## 🚀 Como Corrigir

### Opção 1: Script Automático (Recomendado)
```bash
# Execute o script de correção
fix-services.bat
```

### Opção 2: Manual
```bash
# 1. Pare todos os containers
docker-compose down

# 2. Remova volumes do RabbitMQ (força recriação com novas credenciais)
docker volume rm vms_gtvision_rabbitmq_data

# 3. Reconstrua e inicie
docker-compose up -d --build

# 4. Verifique os logs
docker-compose logs -f backend_worker
docker-compose logs -f rabbitmq
```

## ✅ Verificação de Saúde

### Verificar RabbitMQ
```bash
# Logs do RabbitMQ
docker-compose logs rabbitmq | grep -i "started\|ready"

# Acessar Management UI
# http://localhost:15672
# User: gtvision_user
# Pass: your-rabbitmq-password-here
```

### Verificar Celery Worker
```bash
# Logs do Worker
docker-compose logs backend_worker | tail -50

# Deve mostrar:
# [tasks]
#   . process_detection_message
#   . sync_camera_mediamtx
#   . update_dashboard_stats
```

### Verificar HAProxy
```bash
# Stats do HAProxy
# http://localhost:8404/stats

# Verificar backends:
# - kong_gateway: UP
# - nginx_static: UP
# - mediamtx_hls: UP
# - frontend_dev: UP
```

## 🔍 Diagnóstico Rápido

### Teste de Conectividade RabbitMQ
```bash
# Dentro do container backend
docker-compose exec backend python -c "
from celery import Celery
app = Celery('test', broker='amqp://gtvision_user:your-rabbitmq-password-here@rabbitmq:5672//')
print('✅ Conexão OK!' if app.connection().connect() else '❌ Falha')
"
```

### Teste de Conectividade PostgreSQL
```bash
docker-compose exec backend python manage.py dbshell
# Se conectar, está OK
```

### Teste de Conectividade Redis
```bash
docker-compose exec redis_cache redis-cli ping
# Deve retornar: PONG
```

## 📊 Monitoramento

### Logs em Tempo Real
```bash
# Todos os serviços
docker-compose logs -f

# Apenas erros
docker-compose logs -f | grep -i "error\|warning\|failed"

# Serviço específico
docker-compose logs -f backend_worker
```

### Status dos Containers
```bash
docker-compose ps

# Todos devem estar "Up" e "healthy"
```

## 🆘 Problemas Comuns

### Worker não conecta ao RabbitMQ
1. Verifique credenciais no `.env`
2. Recrie o volume do RabbitMQ
3. Aguarde 30s após iniciar o RabbitMQ

### HAProxy não encontra backends
1. Verifique se todos os serviços estão "healthy"
2. Verifique `docker-compose ps`
3. Aguarde o healthcheck completar (pode levar 1-2 min)

### Migrações não executam
1. Verifique se PostgreSQL está "healthy"
2. Execute manualmente: `docker-compose exec backend python manage.py migrate`
3. Verifique logs: `docker-compose logs backend`

## 📞 Suporte

Se os problemas persistirem:
1. Colete logs: `docker-compose logs > logs.txt`
2. Verifique configurações: `cat .env`
3. Abra uma issue no GitHub com os logs
