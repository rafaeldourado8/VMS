# SYSTEM CONTEXT - GT-Vision VMS
## Documento de Memória e Regras de Negócio Fixas

**Versão:** 1.0  
**Data:** Janeiro 2025  
**Objetivo:** Evitar alucinações e manter consistência arquitetural durante refatoração

---

## 🎯 REGRAS DE NEGÓCIO IMUTÁVEIS

### 1. SEGREGAÇÃO DE TRÁFEGO (SPLIT-BRAIN)
**REGRA CRÍTICA:** Nunca passar vídeo pelo WAF ou Backend Django.

```
✅ CORRETO:
Câmera → HAProxy → MediaMTX → Disco/S3
Cliente → Cloudflare → HAProxy → MediaMTX (bypass total)

❌ ERRADO:
Câmera → Backend Django → MediaMTX
Cliente → WAF → Backend → MediaMTX
```

**Justificativa:** Vídeo é tráfego de alta largura de banda. Passar pelo WAF/Backend causa:
- Latência adicional (>500ms)
- Sobrecarga de CPU no backend
- Gargalo de rede
- Custos desnecessários de processamento

### 2. RETENÇÃO DE DADOS
- **Gravações de vídeo:** 7 dias (padrão) - CONFIGURÁVEL por câmera
- **Detecções de IA:** 30 dias (padrão) - CONFIGURÁVEL
- **Logs de sistema:** 14 dias
- **Métricas Redis:** 24 horas (TTL automático)

### 3. LIMITES DE ESCALA (MVP - 250 Câmeras)
- **Câmeras simultâneas:** 250 (meta MVP)
- **Resolução padrão:** 1920x1080 @ 25fps
- **Bitrate médio:** 2-4 Mbps por câmera
- **Largura de banda total:** ~1 Gbps (250 câmeras × 4 Mbps)
- **Armazenamento diário:** ~8.6 TB (250 câmeras × 7 dias × 5GB/dia)

### 4. PROCESSAMENTO DE IA
- **Frequência de análise:** 1 frame/segundo (não processar todos os frames)
- **Tipos de detecção:** LPR (placas), contagem de pessoas/veículos
- **Latência aceitável:** <2 segundos (da captura até notificação)
- **Worker Python:** Leve, apenas orquestra - não faz transcodificação

### 5. CACHE E PERFORMANCE
- **Cache de API (Redis):** 5 segundos (listagens/dashboard)
- **Cache de status de câmeras:** 15 segundos
- **Timeout de conexão RTSP:** 10 segundos
- **Reconexão automática:** 3 tentativas com backoff exponencial

---

## 🏗️ ARQUITETURA ATUAL (Estado Inicial)

### Stack Tecnológica
```yaml
Frontend:
  - React 18 + TypeScript
  - Vite (build tool)
  - TanStack Query (data fetching)
  - Zustand (state management)
  - Tailwind CSS + shadcn/ui

Backend:
  - Django 5.0 + DRF
  - PostgreSQL 15 (com réplicas de leitura)
  - Redis 7 (cache + session)
  - RabbitMQ 3.13 (message broker)
  - Celery (workers assíncronos)

Gateway:
  - FastAPI (proxy inteligente + ingestão)
  - SQLAlchemy Core (async)
  - Redis (cache)

Streaming:
  - MediaMTX (RTSP/HLS/WebRTC)
  - FFmpeg (transcodificação quando necessário)

Proxy:
  - Nginx (atual - será substituído por HAProxy)
```

### Fluxo de Dados Atual
```
1. INGESTÃO DE VÍDEO:
   Câmera RTSP → MediaMTX → Gravação em disco
   
2. VISUALIZAÇÃO:
   Cliente → Nginx → MediaMTX (HLS/WebRTC)
   
3. API/DADOS:
   Cliente → Nginx → Gateway (FastAPI) → Backend (Django)
   
4. IA:
   Worker Python → Extrai frame do RTSP → Serviço IA → Gateway → DB
```

---

## 🔧 CONFIGURAÇÕES CRÍTICAS

### MediaMTX (mediamtx.yml)
```yaml
# CONFIGURÁVEL: Segmento HLS
hlsSegmentDuration: 1s  # Menor = menor latência, maior carga
hlsSegmentCount: 5      # Buffer de segmentos

# CONFIGURÁVEL: Retenção de gravação
recordDeleteAfter: 7d   # Aumentar consome mais disco

# CONFIGURÁVEL: Formato de gravação
recordFormat: fmp4      # fmp4 = moderno, mpegts = compatível
```

### Nginx (nginx.conf)
```nginx
# CONFIGURÁVEL: Conexões simultâneas
worker_connections 4096;  # Aumentar para mais clientes

# CONFIGURÁVEL: Timeout de proxy
proxy_read_timeout 180s;  # Aumentar se streams travam

# CONFIGURÁVEL: Buffer de proxy
proxy_buffers 8 16k;      # Aumentar para streams de alta qualidade
```

### Backend (settings.py)
```python
# CONFIGURÁVEL: Workers Celery
CELERY_WORKER_CONCURRENCY = 2  # Aumentar para mais processamento paralelo

# CONFIGURÁVEL: Timeout de tasks
CELERY_TASK_TIME_LIMIT = 1800  # 30 minutos

# CONFIGURÁVEL: Cache TTL
CACHE_TTL = 5  # Segundos (Gateway FastAPI)
```

### PostgreSQL
```sql
-- CONFIGURÁVEL: Connection pool (PgBouncer)
max_client_conn = 1000
default_pool_size = 25

-- CONFIGURÁVEL: Índices críticos
CREATE INDEX idx_deteccoes_camera_timestamp ON deteccoes(camera_id, timestamp DESC);
CREATE INDEX idx_deteccoes_timestamp ON deteccoes(timestamp DESC);
```

---

## 🚨 PONTOS DE ATENÇÃO (GARGALOS CONHECIDOS)

### 1. FFmpeg no Gateway
**Problema:** Gateway atual usa FFmpeg para extrair frames.  
**Impacto:** Alto uso de CPU, não escala para 250 câmeras.  
**Solução:** Mover extração de frames para workers dedicados ou usar MediaMTX API.

### 2. Nginx como Proxy Único
**Problema:** Nginx atual faz tudo (API + vídeo).  
**Impacto:** Vídeo compete com API por recursos.  
**Solução:** HAProxy na frente para segregar tráfego.

### 3. Django ORM em Queries Pesadas
**Problema:** ORM gera queries não otimizadas em listagens grandes.  
**Impacto:** Latência >500ms em dashboards.  
**Solução:** Usar raw SQL ou SQLAlchemy Core para queries críticas.

### 4. Frontend Pesado
**Problema:** Muitas bibliotecas, bundle grande (>2MB).  
**Impacto:** Carregamento lento em redes lentas.  
**Solução:** Code splitting, lazy loading, remover libs desnecessárias.

### 5. Falta de Observabilidade
**Problema:** Sem métricas centralizadas (Prometheus/Grafana).  
**Impacto:** Difícil identificar gargalos em produção.  
**Solução:** Adicionar exporters e dashboards.

---

## 📊 MÉTRICAS DE SUCESSO (MVP)

### Performance
- [ ] Latência de API: <100ms (p95)
- [ ] Latência de vídeo (HLS): <3 segundos
- [ ] Latência de vídeo (WebRTC): <500ms
- [ ] Throughput de ingestão: >1000 detecções/segundo
- [ ] Uptime: >99.5%

### Escala
- [ ] 250 câmeras simultâneas estáveis
- [ ] 100+ usuários concorrentes
- [ ] 50+ streams simultâneos por usuário

### Recursos
- [ ] CPU: <70% em carga normal
- [ ] RAM: <80% em carga normal
- [ ] Disco: <85% de uso
- [ ] Rede: <80% da capacidade

---

## 🔐 SEGURANÇA

### Autenticação
- JWT com refresh token (7 dias)
- Access token curto (60 minutos)
- Blacklist de tokens revogados (Redis)

### Autorização
- RBAC (Role-Based Access Control)
- Permissões granulares por câmera
- Auditoria de ações críticas

### Rede
- HTTPS obrigatório em produção
- CORS restrito a domínios conhecidos
- Rate limiting: 100 req/min por IP (API)
- Rate limiting: Sem limite (vídeo - HAProxy)

### Dados Sensíveis
- Senhas RTSP criptografadas (Fernet)
- Credenciais em variáveis de ambiente
- Logs sem informações sensíveis

---

## 🔄 FLUXO DE DEPLOY

### Desenvolvimento
```bash
docker-compose up -d
# Acesso: http://localhost
```

### Staging
```bash
docker-compose -f docker-compose.staging.yml up -d
# Acesso: https://staging.gtvision.com
```

### Produção
```bash
# Kubernetes com Helm
helm upgrade --install gtvision ./k8s/helm -f values.prod.yaml
# Acesso: https://gtvision.com
```

---

## 📝 CONVENÇÕES DE CÓDIGO

### Nomenclatura
- **Câmeras no MediaMTX:** `cam_{id}` (ex: cam_1, cam_42)
- **Chaves Redis:** `{tipo}:{id}:{atributo}` (ex: camera:1:status)
- **Filas Celery:** `{dominio}_{acao}` (ex: detection_ingest)

### Estrutura de Pastas
```
backend/
  apps/           # Django apps (domínios)
  config/         # Settings, URLs, WSGI
  streaming_integration/  # Integração MediaMTX

gateway/
  services/       # Lógica de negócio
  main.py         # FastAPI app

frontend/
  src/
    components/   # Componentes reutilizáveis
    pages/        # Páginas/rotas
    hooks/        # Custom hooks
    store/        # Estado global
```

### Git
- **Branches:** `feature/`, `bugfix/`, `hotfix/`
- **Commits:** Conventional Commits (feat, fix, docs, refactor)
- **PRs:** Obrigatório code review + CI pass

---

## 🎯 PRÓXIMOS PASSOS (Roadmap)

Ver arquivo `tarefas.md` para detalhamento técnico.

**Fases:**
1. Infraestrutura Core (HAProxy, segregação de rotas)
2. Backend & Ingestão (otimização de workers)
3. Frontend (leveza e performance)
4. Observabilidade (Prometheus, Grafana, testes de carga)

---

## 📚 REFERÊNCIAS

- [MediaMTX Docs](https://github.com/bluenviron/mediamtx)
- [HAProxy Best Practices](https://www.haproxy.com/documentation/)
- [Django Performance](https://docs.djangoproject.com/en/5.0/topics/performance/)
- [HLS Spec](https://datatracker.ietf.org/doc/html/rfc8216)
- [WebRTC Spec](https://webrtc.org/getting-started/overview)

---

**IMPORTANTE:** Este documento deve ser consultado antes de qualquer mudança arquitetural significativa.
