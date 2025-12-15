# 🚀 ROADMAP TÉCNICO - GT-Vision Split-Brain Architecture

**Meta:** MVP para 250 câmeras até final de Janeiro 2025  
**Arquitetura:** Split-Brain (segregação total de tráfego de vídeo vs API)

---

## 📋 FASE 1: INFRAESTRUTURA CORE (Semana 1-2)

### 1.1 Implementar HAProxy como Load Balancer Principal
**Objetivo:** Segregar tráfego de vídeo do tráfego de API na entrada.

**Tarefas:**
- [ ] Criar `haproxy/haproxy.cfg` com ACLs para detectar rotas de vídeo
- [ ] Configurar backend para MediaMTX (porta 8888 HLS, 8889 WebRTC, 8554 RTSP)
- [ ] Configurar backend para API (Kong/WAF → Gateway → Django)
- [ ] Configurar backend para Frontend (Nginx estático)
- [ ] Adicionar health checks para todos backends
- [ ] Configurar sticky sessions para WebRTC
- [ ] Adicionar ao `docker-compose.yml` como serviço principal (porta 80/443)

**Arquivos a criar/modificar:**
```
haproxy/
  ├── haproxy.cfg          # Configuração principal
  └── Dockerfile           # Se necessário customização
docker-compose.yml         # Adicionar serviço haproxy
.env                       # Variáveis HAProxy
```

**Regras de roteamento (ACLs):**
```haproxy
# CONFIGURÁVEL: Ajustar paths conforme necessário
acl is_video path_beg /hls/ /stream/ /ws/live/
acl is_video path_end .m3u8 .ts .mp4
acl is_rtsp dst_port 8554
acl is_api path_beg /api/ /admin/ /fast-api/
```

**Validação:**
- [ ] `curl http://localhost/hls/cam_1/index.m3u8` → MediaMTX direto
- [ ] `curl http://localhost/api/cameras/` → Gateway → Django
- [ ] Verificar logs HAProxy: tráfego segregado corretamente

---

### 1.2 Otimizar MediaMTX para 250 Câmeras
**Objetivo:** Garantir que MediaMTX suporte carga sem gargalos.

**Tarefas:**
- [ ] Ajustar `mediamtx.yml` para alta concorrência
- [ ] Configurar gravação em disco com rotação automática (7 dias)
- [ ] Habilitar API de métricas (porta 9998)
- [ ] Configurar paths dinâmicos para câmeras (`cam_{id}`)
- [ ] Testar reconexão automática de streams RTSP
- [ ] Configurar HLS com segmentos otimizados

**Configurações críticas:**
```yaml
# CONFIGURÁVEL: Ajustar conforme hardware
readTimeout: 10s
writeTimeout: 10s
writeQueueSize: 1024        # Aumentado de 512 para 250 câmeras

# HLS otimizado
hlsSegmentDuration: 2s      # CONFIGURÁVEL: 1s=baixa latência, 2s=menos carga
hlsSegmentCount: 3          # CONFIGURÁVEL: Menor buffer, menos memória
hlsSegmentMaxSize: 50M

# Gravação
record: yes
recordPath: /recordings/%path/%Y-%m-%d_%H-%M-%S
recordFormat: fmp4
recordDeleteAfter: 7d       # CONFIGURÁVEL: Retenção de vídeo
```

**Validação:**
- [ ] Testar 10 câmeras simultâneas
- [ ] Verificar uso de CPU/RAM com `docker stats`
- [ ] Confirmar gravações em `/recordings`
- [ ] Testar API: `curl http://mediamtx:9997/v3/paths/list`

---

### 1.3 Configurar Nginx como Servidor Estático
**Objetivo:** Nginx serve apenas frontend e arquivos estáticos (não faz proxy de vídeo).

**Tarefas:**
- [ ] Simplificar `nginx/nginx.conf` removendo proxies de vídeo
- [ ] Manter apenas: frontend, /static/, /media/
- [ ] Configurar cache agressivo para assets (7 dias)
- [ ] Adicionar compressão gzip/brotli
- [ ] Configurar HTTP/2

**Novo nginx.conf (simplificado):**
```nginx
# CONFIGURÁVEL: worker_connections para mais clientes
worker_processes auto;
events {
    worker_connections 2048;  # Reduzido, não serve mais vídeo
}

http {
    # Cache de assets
    location /static/ {
        alias /var/www/static/;
        expires 7d;             # CONFIGURÁVEL: Cache de assets
        add_header Cache-Control "public, immutable";
    }
    
    # Frontend SPA
    location / {
        root /var/www/frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

**Validação:**
- [ ] Frontend carrega em `http://localhost`
- [ ] Assets estáticos servidos com cache headers
- [ ] Verificar que vídeo NÃO passa por Nginx

---

## 📋 FASE 2: BACKEND & INGESTÃO (Semana 2-3)

### 2.1 Otimizar Workers de IA (Extração de Frames)
**Objetivo:** Remover FFmpeg do Gateway, criar workers dedicados leves.

**Tarefas:**
- [ ] Criar `backend/apps/ai_workers/frame_extractor.py`
- [ ] Usar MediaMTX API para obter snapshot em vez de FFmpeg
- [ ] Configurar Celery queue dedicada: `ai_frame_extraction`
- [ ] Implementar rate limiting: 1 frame/segundo por câmera
- [ ] Adicionar retry logic com backoff exponencial
- [ ] Enviar frame para serviço IA externo via HTTP POST

**Novo worker (pseudo-código):**
```python
# CONFIGURÁVEL: FRAME_RATE = 1 frame/segundo
@celery_app.task(queue='ai_frame_extraction')
def extract_and_analyze_frame(camera_id: int):
    # Usa MediaMTX API em vez de FFmpeg
    snapshot_url = f"{MEDIAMTX_API}/v3/paths/get/cam_{camera_id}/snapshot"
    response = httpx.get(snapshot_url, timeout=5)
    
    if response.status_code == 200:
        frame_bytes = response.content
        # Envia para IA
        ai_response = httpx.post(AI_SERVICE_URL, files={'image': frame_bytes})
        # Processa resultado
        save_detection(camera_id, ai_response.json())
```

**Validação:**
- [ ] Worker consome <50MB RAM por câmera
- [ ] CPU <10% por worker (sem FFmpeg)
- [ ] Latência <2s (captura → detecção salva)

---

### 2.2 Otimizar Ingestão de Detecções (Gateway FastAPI)
**Objetivo:** Suportar >1000 detecções/segundo sem perda.

**Tarefas:**
- [ ] Implementar batch insert no `gateway/main.py`
- [ ] Adicionar fila Redis para buffer (se DB lento)
- [ ] Usar connection pooling no PostgreSQL (PgBouncer)
- [ ] Adicionar índices no banco (camera_id, timestamp)
- [ ] Implementar rate limiting por câmera (evitar spam)

**Otimização de ingestão:**
```python
# CONFIGURÁVEL: BATCH_SIZE para ajustar throughput vs latência
BATCH_SIZE = 100
BATCH_TIMEOUT = 1.0  # segundos

# Buffer em memória (ou Redis)
detection_buffer = []

@app.post("/fast-api/ingest/lpr")
async def ingest_lpr_detection(detection: LPRDetection):
    detection_buffer.append(detection)
    
    if len(detection_buffer) >= BATCH_SIZE:
        await flush_buffer()
    
    return {"status": "queued"}

async def flush_buffer():
    if not detection_buffer:
        return
    
    # Batch insert (muito mais rápido)
    query = detections_table.insert()
    await database_writer.execute_many(query, detection_buffer)
    detection_buffer.clear()
```

**Validação:**
- [ ] Teste de carga: 1000 req/s com Locust
- [ ] Latência p95 <50ms
- [ ] Zero perda de dados

---

### 2.3 Implementar PgBouncer (Connection Pooling)
**Objetivo:** Reduzir overhead de conexões ao PostgreSQL.

**Tarefas:**
- [ ] Adicionar serviço `pgbouncer` ao `docker-compose.yml`
- [ ] Configurar pool de 100 conexões
- [ ] Apontar Django e Gateway para PgBouncer (porta 6432)
- [ ] Configurar modo `transaction` (melhor performance)

**docker-compose.yml:**
```yaml
pgbouncer:
  image: pgbouncer/pgbouncer:latest
  environment:
    - DATABASES_HOST=postgres_db
    - DATABASES_PORT=5432
    - DATABASES_USER=${POSTGRES_USER}
    - DATABASES_PASSWORD=${POSTGRES_PASSWORD}
    - DATABASES_DBNAME=${POSTGRES_DB}
    - PGBOUNCER_POOL_MODE=transaction
    - PGBOUNCER_MAX_CLIENT_CONN=1000    # CONFIGURÁVEL
    - PGBOUNCER_DEFAULT_POOL_SIZE=25    # CONFIGURÁVEL
```

**Validação:**
- [ ] Django conecta via PgBouncer
- [ ] Verificar `SHOW POOLS;` no PgBouncer
- [ ] Latência de queries mantida ou melhorada

---

### 2.4 Otimizar Queries Django (Gargalos Conhecidos)
**Objetivo:** Reduzir latência de listagens e dashboards.

**Tarefas:**
- [ ] Adicionar `select_related()` e `prefetch_related()` em ViewSets
- [ ] Criar índices compostos no PostgreSQL
- [ ] Usar `only()` e `defer()` para reduzir campos carregados
- [ ] Implementar paginação cursor-based para listas grandes
- [ ] Cachear queries pesadas no Redis (TTL 5s)

**Índices críticos:**
```sql
-- CONFIGURÁVEL: Ajustar conforme queries mais frequentes
CREATE INDEX CONCURRENTLY idx_deteccoes_camera_ts 
  ON deteccoes(camera_id, timestamp DESC);

CREATE INDEX CONCURRENTLY idx_deteccoes_ts 
  ON deteccoes(timestamp DESC) 
  WHERE timestamp > NOW() - INTERVAL '7 days';

CREATE INDEX CONCURRENTLY idx_cameras_ativa 
  ON cameras(ativa) 
  WHERE ativa = true;
```

**Validação:**
- [ ] `EXPLAIN ANALYZE` em queries lentas
- [ ] Latência de listagem <100ms
- [ ] Dashboard carrega em <500ms

---

## 📋 FASE 3: FRONTEND (Semana 3)

### 3.1 Otimizar Bundle Size (Code Splitting)
**Objetivo:** Reduzir bundle de >2MB para <500KB (gzipped).

**Tarefas:**
- [ ] Analisar bundle com `npm run build -- --analyze`
- [ ] Implementar lazy loading de rotas
- [ ] Remover bibliotecas não utilizadas
- [ ] Substituir bibliotecas pesadas por alternativas leves
- [ ] Configurar tree-shaking no Vite

**Otimizações:**
```typescript
// Lazy loading de páginas
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Cameras = lazy(() => import('./pages/Cameras'));

// Remover libs pesadas
// ❌ moment.js (500KB) → ✅ date-fns (10KB)
// ❌ lodash completo → ✅ lodash-es (tree-shakeable)
```

**Validação:**
- [ ] Bundle principal <200KB (gzipped)
- [ ] Chunks de rotas <100KB cada
- [ ] Lighthouse score >90

---

### 3.2 Otimizar Player de Vídeo (HLS.js)
**Objetivo:** Player leve com overlay de detecções via Canvas.

**Tarefas:**
- [ ] Usar HLS.js nativo (sem wrappers pesados)
- [ ] Implementar Canvas overlay para bounding boxes
- [ ] Adicionar fallback para WebRTC (baixa latência)
- [ ] Implementar lazy loading de players (só carrega quando visível)
- [ ] Otimizar re-renders com `React.memo()`

**Player otimizado:**
```typescript
// CONFIGURÁVEL: HLS_BUFFER_SIZE para ajustar latência
const HLS_CONFIG = {
  maxBufferLength: 10,        // CONFIGURÁVEL: Menor = menos latência
  maxMaxBufferLength: 20,
  liveSyncDuration: 3,
};

const VideoPlayer = React.memo(({ cameraId }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Renderiza bounding boxes no Canvas (não no DOM)
  const drawDetections = useCallback((detections) => {
    const ctx = canvasRef.current?.getContext('2d');
    // ... desenha retângulos
  }, []);
  
  return (
    <>
      <video ref={videoRef} />
      <canvas ref={canvasRef} />
    </>
  );
});
```

**Validação:**
- [ ] Player carrega em <1s
- [ ] Overlay de detecções sem lag
- [ ] Suporta 16 streams simultâneos sem travar

---

### 3.3 Implementar Virtual Scrolling (Listas Grandes)
**Objetivo:** Renderizar apenas itens visíveis em listas de câmeras/detecções.

**Tarefas:**
- [ ] Instalar `@tanstack/react-virtual`
- [ ] Implementar em lista de câmeras
- [ ] Implementar em lista de detecções
- [ ] Adicionar skeleton loading

**Validação:**
- [ ] Lista de 1000 itens renderiza instantaneamente
- [ ] Scroll suave (60fps)

---

## 📋 FASE 4: OBSERVABILIDADE & TESTES (Semana 4)

### 4.1 Implementar Prometheus + Grafana
**Objetivo:** Métricas centralizadas para identificar gargalos.

**Tarefas:**
- [ ] Adicionar Prometheus ao `docker-compose.yml`
- [ ] Configurar exporters: node_exporter, postgres_exporter, redis_exporter
- [ ] Expor métricas do Django (django-prometheus)
- [ ] Expor métricas do MediaMTX (porta 9998)
- [ ] Criar dashboards Grafana: CPU, RAM, Rede, Latência, Throughput

**docker-compose.yml:**
```yaml
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    - prometheus_data:/prometheus
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana:latest
  volumes:
    - grafana_data:/var/lib/grafana
    - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
  ports:
    - "3000:3000"
```

**Validação:**
- [ ] Métricas visíveis em Prometheus
- [ ] Dashboards funcionais em Grafana
- [ ] Alertas configurados (CPU >80%, Disco >85%)

---

### 4.2 Testes de Carga (Locust)
**Objetivo:** Validar que sistema suporta 250 câmeras + 100 usuários.

**Tarefas:**
- [ ] Criar `tests/load/api_load.py` (Locust)
- [ ] Simular 100 usuários acessando dashboard
- [ ] Simular 1000 detecções/segundo
- [ ] Simular 50 streams simultâneos
- [ ] Medir latência p95, p99
- [ ] Identificar gargalos

**Cenários de teste:**
```python
# CONFIGURÁVEL: Ajustar conforme meta de performance
class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/api/analytics/dashboard/")
    
    @task(2)
    def list_cameras(self):
        self.client.get("/api/cameras/")
    
    @task(1)
    def view_detections(self):
        self.client.get("/api/deteccoes/")
```

**Validação:**
- [ ] API: p95 <100ms, p99 <200ms
- [ ] Ingestão: >1000 req/s sem erros
- [ ] Vídeo: latência <3s (HLS)
- [ ] Zero crashes ou timeouts

---

### 4.3 Testes de Resiliência
**Objetivo:** Sistema se recupera de falhas automaticamente.

**Tarefas:**
- [ ] Testar queda de PostgreSQL (failover para réplica)
- [ ] Testar queda de Redis (reconexão automática)
- [ ] Testar queda de MediaMTX (reconexão de câmeras)
- [ ] Testar queda de câmera (health check detecta)
- [ ] Testar sobrecarga (rate limiting funciona)

**Validação:**
- [ ] Downtime <30s em falhas de componentes
- [ ] Dados não são perdidos
- [ ] Alertas são disparados

---

## 📊 CHECKLIST FINAL (MVP Ready)

### Performance
- [ ] API: p95 <100ms
- [ ] Vídeo HLS: latência <3s
- [ ] Vídeo WebRTC: latência <500ms
- [ ] Ingestão: >1000 detecções/s
- [ ] Frontend: Lighthouse >90

### Escala
- [ ] 250 câmeras simultâneas estáveis
- [ ] 100 usuários concorrentes
- [ ] 50 streams simultâneos por usuário

### Recursos
- [ ] CPU <70% (carga normal)
- [ ] RAM <80% (carga normal)
- [ ] Disco <85%
- [ ] Rede <80% capacidade

### Observabilidade
- [ ] Prometheus coletando métricas
- [ ] Grafana com dashboards
- [ ] Alertas configurados
- [ ] Logs centralizados

### Segurança
- [ ] HTTPS em produção
- [ ] JWT funcionando
- [ ] Rate limiting ativo
- [ ] Senhas criptografadas

---

## 🔧 CONFIGURAÇÕES PARA AJUSTE FINO

### HAProxy
```
# CONFIGURÁVEL: Timeouts
timeout connect 5s
timeout client 30s
timeout server 30s
timeout tunnel 1h    # Para WebRTC/WebSocket
```

### MediaMTX
```yaml
# CONFIGURÁVEL: Performance vs Latência
hlsSegmentDuration: 2s    # 1s=baixa latência, 4s=menos CPU
writeQueueSize: 1024      # Aumentar se drops de frames
```

### PostgreSQL
```sql
-- CONFIGURÁVEL: Tuning para 250 câmeras
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 16MB
maintenance_work_mem = 512MB
max_connections = 200
```

### Redis
```
# CONFIGURÁVEL: Memória
maxmemory 512mb           # Aumentar se cache misses
maxmemory-policy allkeys-lru
```

### Celery
```python
# CONFIGURÁVEL: Workers
CELERY_WORKER_CONCURRENCY = 4    # CPU cores
CELERY_WORKER_PREFETCH_MULTIPLIER = 2
```

---

## 📅 CRONOGRAMA SUGERIDO

| Semana | Fase | Entregas |
|--------|------|----------|
| 1 | Infra Core | HAProxy, MediaMTX otimizado, Nginx simplificado |
| 2 | Backend | Workers IA, PgBouncer, Queries otimizadas |
| 3 | Frontend | Bundle otimizado, Player leve, Virtual scroll |
| 4 | Observabilidade | Prometheus, Grafana, Testes de carga |

**Data de entrega:** Final de Janeiro 2025

---

## 🚨 RISCOS E MITIGAÇÕES

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| MediaMTX não aguenta 250 câmeras | Alto | Testar com 50, 100, 150 incrementalmente |
| Disco enche rápido (8TB/semana) | Alto | Implementar limpeza automática, alertas |
| Latência de rede alta | Médio | CDN para vídeo, compressão |
| PostgreSQL lento | Alto | PgBouncer, índices, réplicas de leitura |
| Frontend pesado | Médio | Code splitting, lazy loading |

---

**PRÓXIMO PASSO:** Começar pela Fase 1.1 (HAProxy)
