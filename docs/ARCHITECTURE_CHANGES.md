# Mudanças de Arquitetura - VMS

## 1. Gateway Unificado (HAProxy)

### Antes
- HAProxy (porta 80)
- Kong Gateway (porta 8002)
- Nginx (arquivos estáticos)

### Depois
- **HAProxy** como único ponto de entrada (porta 80)
- Kong acessível apenas via HAProxy (sem porta exposta)
- Nginx continua servindo estáticos via HAProxy

### Benefícios
✅ Ponto único de entrada  
✅ Reduz complexidade  
✅ Melhor controle de roteamento  
✅ Facilita SSL/TLS termination  

### Acesso
```bash
# Frontend
http://localhost/

# Backend API
http://localhost/api/

# Admin Django
http://localhost/admin/

# Streaming
http://localhost/streaming/

# HLS
http://localhost/hls/cam_1/

# Stats HAProxy
http://localhost:8404/stats
```

---

## 2. PostgreSQL com Réplicas Reais

### Antes
```yaml
postgres_db: (único container)
DB_HOST_REPLICA_1=postgres_db  # fake
DB_HOST_REPLICA_2=postgres_db  # fake
```

### Depois
```yaml
postgres_db:           # PRIMARY (write)
postgres_replica_1:    # REPLICA 1 (read-only)
postgres_replica_2:    # REPLICA 2 (read-only)
```

### Configuração

1. **Atualizar .env**
```bash
cp .env.example .env
# Editar POSTGRES_REPLICATION_PASSWORD
```

2. **Iniciar serviços**
```bash
docker-compose up -d postgres_db
docker-compose up -d postgres_replica_1 postgres_replica_2
```

3. **Configurar replicação**
```bash
# Linux/Mac
bash scripts/init_postgres_replication.sh

# Windows
scripts\init_postgres_replication.bat
```

4. **Verificar status**
```bash
docker exec gtvision_postgres_primary psql -U gtvision_user -c "SELECT * FROM pg_stat_replication;"
```

### Uso no Código

**Django (Write)**
```python
# Usa automaticamente o PRIMARY
Camera.objects.create(name="Cam 1")
```

**Django (Read)**
```python
# Usa réplicas via db_router.py
cameras = Camera.objects.using('replica').all()
```

**FastAPI (Read)**
```python
# Balanceamento automático entre réplicas
DB_HOST_READERS = "postgres_replica_1,postgres_replica_2"
```

### Monitoramento

```bash
# Lag de replicação
docker exec gtvision_postgres_primary psql -U gtvision_user -c "
SELECT 
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state
FROM pg_stat_replication;
"

# Status das réplicas
docker exec gtvision_postgres_replica_1 psql -U gtvision_user -c "SELECT pg_is_in_recovery();"
```

---

## 3. .gitignore Atualizado

### Adicionado
```
hls_cache/      # Cache HLS gerado em runtime
recordings/     # Gravações de vídeo
```

### Motivo
- Arquivos grandes (vídeos)
- Gerados automaticamente
- Específicos de cada ambiente

---

## Migração

### Passo a Passo

1. **Backup do banco atual**
```bash
docker exec gtvision_postgres pg_dump -U gtvision_user gtvision_db > backup.sql
```

2. **Parar serviços**
```bash
docker-compose down
```

3. **Atualizar arquivos**
```bash
git pull
cp .env.example .env
# Editar .env com suas credenciais
```

4. **Iniciar nova arquitetura**
```bash
docker-compose up -d
```

5. **Configurar replicação**
```bash
scripts/init_postgres_replication.bat  # Windows
# ou
bash scripts/init_postgres_replication.sh  # Linux/Mac
```

6. **Verificar**
```bash
# HAProxy stats
curl http://localhost:8404/stats

# Replicação
docker exec gtvision_postgres_primary psql -U gtvision_user -c "SELECT * FROM pg_stat_replication;"
```

---

## Troubleshooting

### Réplicas não conectam
```bash
# Verificar logs
docker logs gtvision_postgres_replica_1

# Recriar réplica
docker-compose stop postgres_replica_1
docker volume rm vms_gtvision_pg_replica_1
docker-compose up -d postgres_replica_1
```

### HAProxy não roteia
```bash
# Verificar backends
curl http://localhost:8404/stats

# Testar diretamente
curl http://localhost/api/health
```

### Kong não responde
```bash
# Verificar via HAProxy
docker logs gtvision_haproxy

# Testar Kong diretamente (dentro da rede)
docker exec gtvision_haproxy wget -O- http://kong:8000
```
