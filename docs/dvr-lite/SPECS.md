# 📋 DVR-Lite - Especificações Técnicas

## 🎯 Cenário de Uso

### Infraestrutura
- **1 VPS** (servidor único)
- **Sistema:** Ubuntu 22.04 LTS
- **Deploy:** Docker Compose

### Capacidade
- **50 câmeras** total no sistema
- **1 admin** (dono do sistema)
- **100 sub-usuários** (operadores)
- **Permissão:** Cada sub-usuário vê apenas 1 câmera

---

## 💻 Requisitos de Hardware (VPS)

### Configuração Mínima
```
CPU: 8 cores (16 threads)
RAM: 16 GB
Disco: 500 GB SSD
Banda: 500 Mbps
```

### Configuração Recomendada
```
CPU: 12 cores (24 threads)
RAM: 32 GB
Disco: 1 TB NVMe SSD
Banda: 1 Gbps
```

### Provedores Sugeridos
- **Hetzner:** CPX51 (~€50/mês) ou CCX33 (~€70/mês)
- **OVH:** VPS Elite (~€60/mês)
- **Contabo:** VPS L (~€30/mês)
- **DigitalOcean:** Droplet 16GB (~$96/mês)

---

## 📊 Cálculos de Capacidade

### Streaming (50 câmeras)
```
Bitrate por câmera: 2 Mbps (média)
Total streaming: 50 × 2 = 100 Mbps

Com 20 usuários assistindo simultaneamente:
20 usuários × 2 Mbps = 40 Mbps
```

### Gravação (7 dias)
```
Por câmera/dia: 2 Mbps × 86400s ÷ 8 = 21.6 GB/dia
50 câmeras/dia: 50 × 21.6 = 1,080 GB/dia = 1.08 TB/dia
7 dias: 1.08 × 7 = 7.56 TB

Com compressão H.264 (50% economia):
7.56 TB × 0.5 = 3.78 TB necessários
```

### Armazenamento Recomendado
```
Gravações (7 dias): 4 TB
Clipes permanentes: 500 GB
Sistema + Logs: 100 GB
Buffer: 400 GB
----------------------------
Total: 5 TB
```

---

## 👥 Estrutura de Usuários

### Super Admin (Nós - Governança)
- **Acesso:** Todos os sistemas e clientes
- **Permissões:**
  - ✅ Acesso a todas as VPS/clientes
  - ✅ Criar/deletar organizações (clientes)
  - ✅ Ver métricas globais
  - ✅ Gerenciar billing
  - ✅ Suporte técnico
  - ✅ Logs de auditoria

### Admin Cliente (1 por organização)
- **Acesso:** Todas as 50 câmeras da sua organização
- **Permissões:**
  - ✅ Ver todas as câmeras
  - ✅ Criar/editar/deletar câmeras
  - ✅ Criar sub-usuários (até 100)
  - ✅ Gerenciar permissões
  - ✅ Ver todos os clipes
  - ✅ Acessar configurações
  - ❌ Ver outras organizações

### Sub-Usuários (100 por organização)
- **Acesso:** 1 câmera específica
- **Permissões:**
  - ✅ Ver streaming da câmera atribuída
  - ✅ Ver gravações da câmera
  - ✅ Criar clipes (máx 5min)
  - ❌ Ver outras câmeras
  - ❌ Criar/editar câmeras
  - ❌ Criar outros usuários
  - ❌ Acessar configurações

### Distribuição
```
1 Super Admin (nós)
  └── N Organizações (clientes)
       └── 1 Admin por organização
            └── 50 câmeras
                 └── 100 sub-usuários (50 ativos)
```

---

## 🔐 Modelo de Permissões

### Tabela: organizations (multi-tenant)
```sql
id | name           | slug      | max_cameras | max_users | active
---+----------------+-----------+-------------+-----------+-------
1  | Empresa A      | empresa-a | 50          | 100       | true
2  | Empresa B      | empresa-b | 50          | 100       | true
```

### Tabela: users
```sql
id | email                | role        | org_id | parent_user_id
---+----------------------+-------------+--------+---------------
1  | admin@dvrlite.com    | super_admin | NULL   | NULL
2  | admin@empresaa.com   | org_admin   | 1      | NULL
3  | user1@empresaa.com   | sub_user    | 1      | 2
4  | user2@empresaa.com   | sub_user    | 1      | 2
...
102| admin@empresab.com   | org_admin   | 2      | NULL
```

### Tabela: cameras
```sql
id | name      | stream_url | org_id | created_by
---+-----------+------------+--------+-----------
1  | Câmera 1  | rtsp://... | 1      | 2
2  | Câmera 2  | rtsp://... | 1      | 2
...
51 | Câmera 1  | rtsp://... | 2      | 102
```

### Tabela: user_camera_permissions
```sql
user_id | camera_id | can_view | can_playback | can_clip
--------+-----------+----------+--------------+---------
3       | 1         | true     | true         | true
4       | 2         | true     | true         | true
```

---

## 📹 Tipos de Câmeras

### Distribuição Sugerida
```
RTSP (Alta qualidade): 30 câmeras
- Resolução: 1080p
- Bitrate: 2-3 Mbps
- Uso: Áreas críticas

RTMP (Qualidade padrão): 20 câmeras
- Resolução: 720p
- Bitrate: 1-2 Mbps
- Uso: Áreas secundárias
```

---

## 💾 Storage Strategy

### Opção 1: Storage Local (VPS)
```
Disco: 5 TB NVMe SSD
Custo: Incluído no VPS
Backup: Rsync para servidor externo
```

### Opção 2: Storage Híbrido
```
Local (SSD): Últimas 24h (200 GB)
S3/Wasabi: Dias 2-7 (4 TB)
Custo S3: ~$100/mês
Custo Wasabi: ~$25/mês (mais barato)
```

### Opção 3: Storage Externo
```
Wasabi: 5 TB
Custo: ~$30/mês
Latência: +100ms para playback
```

**Recomendação:** Opção 2 (Híbrido) para melhor custo/benefício.

---

## 🚀 Performance Esperada

### Streaming Simultâneo
```
Máximo teórico: 50 usuários (1 por câmera)
Recomendado: 30 usuários simultâneos
Pico esperado: 20 usuários (horário comercial)
```

### Playback Simultâneo
```
Máximo: 10 usuários
Recomendado: 5 usuários
```

### Criação de Clipes
```
Fila: 5 clipes simultâneos
Tempo médio: 30s por clipe de 5min
```

---

## 💰 Custo Total Mensal

### VPS (Hetzner CPX51)
```
CPU: 8 cores
RAM: 16 GB
Disco: 360 GB NVMe
Banda: 20 TB
Custo: €50/mês (~$55/mês)
```

### Storage Adicional (Wasabi)
```
5 TB para gravações
Custo: $30/mês
```

### Backup (Opcional)
```
Backblaze B2: 500 GB
Custo: $3/mês
```

### Total
```
VPS: $55/mês
Storage: $30/mês
Backup: $3/mês
-------------------
Total: $88/mês
```

**Por usuário:** $88 ÷ 100 = $0.88/mês/usuário

---

## 📈 Escalabilidade

### Crescimento Vertical (Mesma VPS)
```
Até 100 câmeras: Upgrade para CPX51 (16 cores, 32GB)
Custo: €100/mês (~$110/mês)
```

### Crescimento Horizontal (Multi-VPS)
```
VPS 1: 50 câmeras (Região A)
VPS 2: 50 câmeras (Região B)
Load Balancer: Cloudflare (grátis)
```

---

## 🔧 Configuração do Sistema

### Docker Compose Resources
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
  
  mediamtx:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
  
  postgres_db:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
  
  redis_cache:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
```

### Variáveis de Ambiente
```bash
# Capacidade
MAX_CAMERAS=50
MAX_SUB_USERS=100
MAX_CONCURRENT_STREAMS=30
MAX_CONCURRENT_PLAYBACK=10

# Storage
RECORDING_RETENTION_DAYS=7
LOCAL_STORAGE_PATH=/mnt/recordings
S3_ENABLED=true
S3_BUCKET=empresa-recordings

# Performance
THUMBNAIL_CACHE_TTL=300
STREAM_BUFFER_SIZE=2048
RECORDING_SEGMENT_DURATION=3600
```

---

## 🧪 Testes de Carga

### Teste 1: Streaming
```bash
# Simular 30 usuários assistindo
for i in {1..30}; do
  curl http://vps-ip:8888/camera$i/index.m3u8 &
done
```

### Teste 2: Playback
```bash
# Simular 10 usuários em playback
for i in {1..10}; do
  curl http://vps-ip:8000/api/playback/stream/$i/ &
done
```

### Teste 3: Criação de Clipes
```bash
# Criar 5 clipes simultâneos
for i in {1..5}; do
  curl -X POST http://vps-ip:8000/api/clips/ \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"camera_id": '$i', "start": "2025-01-01T10:00:00", "duration": 300}'
done
```

---

## 📊 Monitoramento

### Métricas Críticas
```
CPU Usage: < 80%
RAM Usage: < 85%
Disk Usage: < 90%
Network In: < 400 Mbps
Network Out: < 400 Mbps
Active Streams: < 30
Active Playbacks: < 10
```

### Alertas
```
CPU > 90%: Escalar VPS
Disk > 95%: Limpar gravações antigas
Streams > 40: Limitar novos streams
```

---

## 🎯 Resumo

```
┌─────────────────────────────────────────────────────────┐
│                    DVR-Lite Specs                       │
├─────────────────────────────────────────────────────────┤
│  Infraestrutura: 1 VPS                                  │
│  Câmeras: 50                                            │
│  Usuários: 1 admin + 100 sub-users                      │
│  Permissão: 1 câmera por sub-user                       │
│  Gravação: 7 dias                                       │
│  Storage: 5 TB (híbrido)                                │
│  Custo: ~$88/mês                                        │
│  Por usuário: $0.88/mês                                 │
└─────────────────────────────────────────────────────────┘
```
