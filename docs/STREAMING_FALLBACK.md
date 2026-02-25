# Sistema de Fallback para Streaming HLS

## Problema

Quando o backend reinicia, o streaming HLS quebra porque:
- MediaMTX perde as configurações de câmeras provisionadas
- Frontend continua tentando acessar streams que não existem mais
- Usuários veem tela preta ou erro de carregamento

## Solução

Sistema de fallback em 4 camadas:

### 1. Persistência no Redis
- Toda câmera provisionada é salva no Redis (`camera:{id}`)
- Ao reiniciar, o streaming service restaura automaticamente do Redis
- Dados persistidos: `camera_id`, `rtsp_url`, `name`, `enabled`, `stream_path`

### 2. Provisionamento no Startup do Backend
- Script `provision_cameras_startup.py` roda antes do Django iniciar
- Busca todas as câmeras ativas do banco
- Provisiona automaticamente no streaming service
- Garante que câmeras estejam prontas quando backend ficar healthy

### 3. Auto-Provision no Acesso
- Endpoint `/hls/{stream_path}/{file_name}` detecta 404
- Busca câmera no Redis
- Provisiona automaticamente se encontrada
- Retorna stream em ~2 segundos

### 4. Health Check Periódico
- Script `stream_health_check.py` roda a cada 60 segundos
- Compara câmeras do backend com streams no MediaMTX
- Reprovisiona automaticamente câmeras faltantes

## Arquitetura

```
┌─────────────┐
│   Backend   │ ──┐
│   (Django)  │   │
└─────────────┘   │
                  ├──> Redis (Persistência)
┌─────────────┐   │
│  Streaming  │ ──┘
│  (FastAPI)  │ ──> MediaMTX (Streams)
└─────────────┘
       │
       ├──> stream_health_check.py (60s)
       └──> mediamtx_monitor.py (30s)
```

## Fluxo de Recuperação

### Cenário 1: Backend Reinicia
1. Backend inicia
2. `provision_cameras_startup.py` aguarda streaming service
3. Busca todas as câmeras ativas do banco
4. Provisiona cada câmera no streaming service
5. Backend fica healthy
6. Streams disponíveis em ~30 segundos

### Cenário 2: MediaMTX Reinicia
1. `mediamtx_monitor.py` detecta crash
2. Aguarda MediaMTX voltar
3. Reprovisiona todas as câmeras do Redis
4. Streams voltam em ~30 segundos

### Cenário 3: Frontend Acessa Stream Inexistente
1. Frontend tenta acessar `/hls/cam_15/index.m3u8`
2. MediaMTX retorna 404
3. Proxy HLS detecta 404 e busca câmera no Redis
4. Provisiona automaticamente
5. Aguarda 2s e retorna stream
6. Frontend recebe HLS normalmente

### Cenário 4: Inconsistência Detectada
1. `stream_health_check.py` compara backend vs MediaMTX
2. Identifica câmeras faltantes
3. Reprovisiona automaticamente
4. Logs indicam câmeras restauradas

## Testes

### Teste Automático
```bash
tests\test_streaming_fallback.bat
```

### Teste Manual
```bash
# 1. Verificar estado inicial
curl http://localhost:8001/stats

# 2. Reiniciar backend
docker restart gtvision_backend

# 3. Aguardar 15 segundos

# 4. Verificar restauração
curl http://localhost:8001/stats
```

### Teste de Sincronização Forçada
```bash
curl -X POST http://localhost/api/cameras/sync_with_streaming/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Monitoramento

### Logs do Streaming Service
```bash
docker logs -f gtvision_streaming
```

Mensagens esperadas:
- `✅ X câmeras restauradas do Redis` - Restauração automática
- `Provisionando cam_X` - Câmera sendo provisionada

### Logs do Health Check
```bash
docker logs -f gtvision_stream_health
```

Mensagens esperadas:
- `✅ Todas as X câmeras sincronizadas` - Tudo OK
- `⚠️ X câmeras fora de sincronia` - Inconsistência detectada
- `🔄 Reprovisionando cam_X...` - Correção em andamento

### Logs do MediaMTX Monitor
```bash
docker logs -f gtvision_mediamtx_monitor
```

Mensagens esperadas:
- `✅ MediaMTX voltou online` - Recuperação de crash
- `🔄 Reprovisionando X câmeras...` - Restauração após crash

## Configuração

### Variáveis de Ambiente

**Streaming Service:**
```env
REDIS_URL=redis://redis_cache:6379/2
MEDIAMTX_API_URL=http://mediamtx:9997
```

**Health Check:**
```python
CHECK_INTERVAL = 60  # segundos entre verificações
```

**MediaMTX Monitor:**
```python
CHECK_INTERVAL = 30  # segundos entre verificações
```

## Troubleshooting

### Câmeras não restauram após restart
1. Verificar se Redis está rodando: `docker ps | grep redis`
2. Verificar logs: `docker logs gtvision_streaming`
3. Forçar sincronização: `POST /api/cameras/sync_with_streaming/`

### Health check não detecta inconsistências
1. Verificar se serviço está rodando: `docker ps | grep stream_health`
2. Verificar logs: `docker logs gtvision_stream_health`
3. Verificar conectividade: `docker exec gtvision_stream_health curl http://backend:8000/health`

### MediaMTX não reprovisiona após crash
1. Verificar monitor: `docker ps | grep mediamtx_monitor`
2. Verificar logs: `docker logs gtvision_mediamtx_monitor`
3. Restart manual: `docker restart gtvision_mediamtx_monitor`

## Performance

- **Tempo de restauração (backend restart):** ~10 segundos
- **Tempo de restauração (MediaMTX crash):** ~30 segundos
- **Overhead do health check:** <1% CPU, <50MB RAM
- **Overhead do Redis:** ~10MB por 100 câmeras

## Limitações

1. Requer Redis disponível (fallback gracioso se indisponível)
2. Intervalo mínimo de verificação: 30 segundos
3. Não detecta mudanças de RTSP URL (requer reprovisão manual)

## Roadmap

- [ ] Notificação via webhook quando câmera é restaurada
- [ ] Dashboard de status de sincronização
- [ ] Métricas Prometheus para monitoramento
- [ ] Auto-ajuste de intervalo baseado em carga
