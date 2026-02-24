# Portas do VMS - Video Management System

## 🌐 Portas Públicas (Expostas no Host)

| Porta | Serviço | Descrição | Acesso |
|-------|---------|-----------|--------|
| **80** | HAProxy | Gateway principal (HTTP) | http://localhost |
| **8001** | Streaming | API de streaming | http://localhost:8001 |
| **8003** | Storage | API de armazenamento | http://localhost:8003 |
| **8004** | Clips | API de clips/eventos | http://localhost:8004 |
| **8005** | ONVIF | Serviço ONVIF | http://localhost:8005 |
| **8006** | VOD HLS | Video on Demand (HLS) | http://localhost:8006 |
| **8404** | HAProxy Stats | Dashboard HAProxy | http://localhost:8404/stats |
| **8554** | MediaMTX RTSP | Servidor RTSP | rtsp://localhost:8554 |
| **8888** | MediaMTX HLS | Streaming HLS | http://localhost:8888 |
| **8889** | MediaMTX WebRTC | WebRTC | http://localhost:8889 |
| **9996** | MediaMTX Metrics | Métricas Prometheus | http://localhost:9996 |
| **9997** | MediaMTX API | API de controle | http://localhost:9997 |

## 🔒 Portas Internas (Apenas na Rede Docker)

| Porta | Serviço | Descrição |
|-------|---------|-----------|
| 5432 | PostgreSQL | Banco de dados (primary + 2 replicas) |
| 6379 | Redis | Cache e filas |
| 8000 | Backend Django | API principal |
| 8001 | MediaMTX Monitor | Monitor interno |
| 80 | Nginx | Servidor de arquivos estáticos |
| 8000-8001 | Kong Gateway | API Gateway interno |
| 8443-8444 | Kong Gateway | HTTPS interno |

## 📋 Mapeamento de Rotas (via HAProxy - Porta 80)

| Rota | Destino | Descrição |
|------|---------|-----------|
| `/` | Frontend (Nginx) | Interface web |
| `/api/*` | Kong → Backend | API REST |
| `/admin/*` | Kong → Backend | Django Admin |
| `/streaming/*` | Streaming Service | WebSocket + API |
| `/storage/*` | Storage Service | Upload/download |
| `/clips/*` | Clips Service | Eventos/clips |
| `/vod/*` | VOD HLS Service | Gravações |
| `/static/*` | Nginx | Arquivos estáticos |

## 🎥 Fluxo de Vídeo

```
Câmera RTSP → MediaMTX (8554) → Recorder → /recordings/
                ↓
         Streaming (8001) ← Frontend
                ↓
         VOD HLS (8006) ← Player
```

## 🔧 Portas para Desenvolvimento

| Porta | Uso |
|-------|-----|
| 5432 | Conectar ao PostgreSQL diretamente |
| 6379 | Conectar ao Redis diretamente |
| 8000 | Acessar Django sem HAProxy |
| 9997 | API MediaMTX para debug |

## 🚀 Portas para Produção

**Apenas expor:**
- **80** (HTTP) ou **443** (HTTPS)
- **8554** (RTSP) - se câmeras externas precisarem conectar

**Bloquear:**
- Todas as outras portas devem estar acessíveis apenas internamente

## 🔐 Segurança

### Firewall Recomendado (AWS Security Group)

```
Inbound:
- 80/tcp   → 0.0.0.0/0 (HTTP público)
- 443/tcp  → 0.0.0.0/0 (HTTPS público)
- 8554/tcp → [IPs das câmeras] (RTSP)
- 22/tcp   → [Seu IP] (SSH admin)

Outbound:
- All traffic → 0.0.0.0/0
```

## 📊 Monitoramento

| URL | Descrição |
|-----|-----------|
| http://localhost:8404/stats | HAProxy dashboard |
| http://localhost:9996/metrics | MediaMTX Prometheus |
| http://localhost/api/health | Health check geral |

## 🐳 Docker Networks

- **vms_gtvision_network**: Rede principal (bridge)
  - Todos os containers se comunicam internamente
  - Apenas portas mapeadas são expostas ao host
