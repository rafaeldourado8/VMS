# 🔧 Troubleshooting - Sistema VMS

## ❌ Erro: Docker 500 Internal Server Error

### Causa
Docker Desktop com problemas de I/O ou cache corrompido.

### Solução

#### 1. Reiniciar Docker Desktop
```bash
# Fechar Docker Desktop
taskkill /F /IM "Docker Desktop.exe"

# Aguardar 5 segundos

# Abrir Docker Desktop novamente
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

#### 2. Limpar Cache
```bash
docker system prune -f
docker volume prune -f
```

#### 3. Iniciar Sistema Gradualmente
```bash
# Apenas streaming (sem IA)
docker-compose up -d mediamtx streaming redis_cache

# Verificar se funcionou
docker-compose ps

# Adicionar backend
docker-compose up -d postgres_db backend

# Adicionar frontend
docker-compose up -d frontend kong haproxy
```

## 🤖 Serviços de IA (Opcional)

### Iniciar IA Separadamente
```bash
# Infraestrutura de IA
docker-compose up -d rabbitmq_ai redis_ai postgres_ai

# Aguardar 10 segundos

# Workers de IA
docker-compose up -d ai_worker_1
# Se worker_1 funcionar, adicionar worker_2
docker-compose up -d ai_worker_2
```

### Se Build de IA Falhar

#### Opção 1: Usar imagem pré-construída
```bash
# Comentar build no docker-compose.yml
# Usar imagem pronta (se disponível)
```

#### Opção 2: Rodar IA fora do Docker
```bash
cd services/ai_detection

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install torch==2.1.0+cpu torchvision==0.16.0+cpu --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# Configurar variáveis
set RABBITMQ_URL=amqp://ai_user:ai_pass@localhost:5672/
set REDIS_URL=redis://localhost:6379/3
set DB_URL=postgresql://ai_user:ai_pass@localhost:5432/ai_detections

# Rodar
python main.py
```

## 📊 Sistema Mínimo Funcional

### Apenas Streaming (Sem IA)
```yaml
Serviços necessários:
- mediamtx
- streaming
- redis_cache

Recursos:
- CPU: ~3-4 cores
- RAM: ~3-4GB
- 12 câmeras simultâneas
```

### Com Backend (Sem IA)
```yaml
Adicionar:
- postgres_db
- backend
- frontend
- kong
- haproxy

Recursos:
- CPU: ~4-5 cores
- RAM: ~5-6GB
```

### Sistema Completo (Com IA)
```yaml
Adicionar:
- rabbitmq_ai
- redis_ai
- postgres_ai
- ai_worker_1
- ai_worker_2

Recursos:
- CPU: ~6-7 cores
- RAM: ~8-10GB
```

## 🚀 Ordem Recomendada de Inicialização

```bash
# 1. Infraestrutura base
docker-compose up -d redis_cache postgres_db

# 2. Streaming
docker-compose up -d mediamtx streaming

# 3. Backend
docker-compose up -d backend

# 4. Frontend e Gateway
docker-compose up -d frontend kong haproxy

# 5. IA (opcional)
docker-compose up -d rabbitmq_ai redis_ai postgres_ai
docker-compose up -d ai_worker_1
```

## 📝 Verificar Status

```bash
# Status de todos os serviços
docker-compose ps

# Logs de um serviço específico
docker-compose logs -f mediamtx
docker-compose logs -f streaming
docker-compose logs -f ai_worker_1

# Uso de recursos
docker stats

# Health checks
curl http://localhost:8001/health
curl http://localhost:8001/stats
```

## 🔄 Reiniciar Serviço Específico

```bash
# Reiniciar apenas um serviço
docker-compose restart mediamtx
docker-compose restart streaming
docker-compose restart ai_worker_1

# Rebuild e restart
docker-compose up -d --build streaming
```

## 🗑️ Limpar Tudo e Recomeçar

```bash
# Parar tudo
docker-compose down -v

# Limpar cache
docker system prune -af
docker volume prune -f

# Rebuild tudo
docker-compose build --no-cache

# Iniciar
docker-compose up -d
```

---

**Dica**: Se IA não funcionar, o sistema de streaming funciona perfeitamente sem ela!