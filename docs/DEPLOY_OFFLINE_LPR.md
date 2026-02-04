# Deploy - Arquitetura Offline LPR

## Pré-requisitos

- Docker + Docker Compose
- NVIDIA GPU + nvidia-docker (para LPR)
- Câmeras RTSP configuradas

## Passo a Passo

### 1. Atualizar Configuração

O arquivo `mediamtx.yml` já está configurado com:
```yaml
record: yes
recordDeleteAfter: 168h  # 7 dias
```

### 2. Build dos Serviços

```bash
# Storage Service
cd services/storage
docker build -t gtvision/storage:latest .

# LPR Offline (se necessário rebuild)
cd ../lpr
docker build -t gtvision/lpr:latest .
```

### 3. Deploy

```bash
# Subir Storage Service
docker-compose up -d storage

# Aguardar inicialização (30s)
docker-compose logs -f storage

# Subir LPR Offline Worker
docker-compose up -d lpr_offline

# Verificar logs
docker-compose logs -f lpr_offline
```

### 4. Validar

```bash
# Testar Storage API
curl http://localhost:8003/health
curl http://localhost:8003/recordings/stats

# Verificar gravações no disco
ls -lh recordings/cam_*/

# Testar consulta
python tests/test_offline_architecture.py
```

## Estrutura de Diretórios

```
recordings/
├── cam_1/
│   ├── 2025-01-30/
│   │   ├── 10-00-00-123456.mp4
│   │   ├── 11-00-00-234567.mp4
│   │   └── 12-00-00-345678.mp4
│   └── 2025-01-31/
├── cam_2/
│   └── 2025-01-30/
└── cam_3/
```

## Monitoramento

### Logs em Tempo Real

```bash
# Storage Service
docker-compose logs -f storage

# LPR Worker
docker-compose logs -f lpr_offline

# MediaMTX
docker-compose logs -f mediamtx
```

### Estatísticas

```bash
# Armazenamento
curl http://localhost:8003/recordings/stats | jq

# Eventos LPR (últimas 24h)
docker-compose exec postgres_db psql -U gtvision_user -d gtvision_db -c \
  "SELECT COUNT(*), camera_id FROM lpr_events 
   WHERE timestamp > NOW() - INTERVAL '24 hours' 
   GROUP BY camera_id;"
```

### Espaço em Disco

```bash
# Tamanho total de gravações
du -sh recordings/

# Por câmera
du -sh recordings/cam_*/

# Limpeza manual (se necessário)
find recordings/ -type f -mtime +7 -delete
```

## Troubleshooting

### Storage não indexa gravações

```bash
# Verificar permissões
docker-compose exec storage ls -la /recordings

# Forçar scan manual
docker-compose restart storage
```

### LPR não processa

```bash
# Verificar GPU
docker-compose exec lpr_offline nvidia-smi

# Verificar conexão com Storage
docker-compose exec lpr_offline curl http://storage:8003/health

# Verificar banco
docker-compose exec lpr_offline python -c "import asyncpg; print('OK')"
```

### Gravações não aparecem

```bash
# Verificar MediaMTX
curl http://localhost:9997/v3/paths/list \
  -u mediamtx_api_user:GtV\!sionMed1aMTX\$2025 | jq

# Verificar configuração de câmera
curl http://localhost:9997/v3/paths/get/cam_2 \
  -u mediamtx_api_user:GtV\!sionMed1aMTX\$2025 | jq
```

## Performance

### Ajustar Processamento LPR

Editar `lpr_offline_worker.py`:

```python
# Processar mais frames (maior precisão, mais CPU)
skip_frames = int(fps * 1)  # 1 frame/segundo

# Processar menos frames (menor CPU)
skip_frames = int(fps * 5)  # 1 frame a cada 5 segundos

# Ajustar intervalo de busca
start_time = end_time - timedelta(hours=1)  # Apenas última hora
```

### Ajustar Retenção

Editar `mediamtx.yml`:

```yaml
recordDeleteAfter: 336h  # 14 dias
recordDeleteAfter: 720h  # 30 dias
```

## Backup

### Exportar Eventos LPR

```bash
docker-compose exec postgres_db pg_dump \
  -U gtvision_user -d gtvision_db \
  -t lpr_events -t recording_segments \
  > backup_lpr_$(date +%Y%m%d).sql
```

### Restaurar

```bash
docker-compose exec -T postgres_db psql \
  -U gtvision_user -d gtvision_db \
  < backup_lpr_20250130.sql
```

## Escalabilidade

### Múltiplos Workers LPR

```yaml
# docker-compose.yml
lpr_offline_1:
  # ... configuração base
  environment:
    WORKER_ID: 1

lpr_offline_2:
  # ... configuração base
  environment:
    WORKER_ID: 2
```

### Distribuir Câmeras

```python
# lpr_offline_worker.py
worker_id = int(os.getenv("WORKER_ID", 1))
cameras = [c for c in all_cameras if c % 2 == worker_id % 2]
```
