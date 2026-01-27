# Fase 1 - Infraestrutura Base

## Objetivo

Subir ambiente local completo com um comando: NGINX + MediaMTX + Frontend com HLS player.

## Arquitetura

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ :80
       ▼
┌─────────────┐
│    NGINX    │ Reverse Proxy
└──────┬──────┘
       │
       ├─► /          → Frontend (HLS Player)
       └─► /hls/*     → MediaMTX :8888
                           │
                           ▼
                    ┌──────────────┐
                    │   MediaMTX   │
                    │   :8554 RTSP │
                    │   :8888 HLS  │
                    │   :9997 API  │
                    └──────────────┘
```

## Stack

- **NGINX**: Reverse proxy + serve frontend
- **MediaMTX**: Streaming server (RTSP → HLS)
- **Frontend**: HTML + HLS.js (player minimalista)

## Como usar

### 1. Subir ambiente

```bash
cd vms
docker-compose up -d
```

### 2. Testar streams

Abra: **http://localhost**

Digite no campo: `camera_rtsp`, `camera_rtmp` ou `camera_ip`

### 3. Adicionar câmeras via API

As câmeras são adicionadas **dinamicamente via API do MediaMTX**.

O container `ffmpeg_test` adiciona 3 câmeras de teste automaticamente:

- `camera_rtsp`: Câmera Intelbras via RTSP
- `camera_rtmp`: Stream SRS via RTMP
- `camera_ip`: Câmera IP via RTSP

### 4. Verificar câmeras ativas

```bash
curl http://localhost:9997/v3/paths/list
```

### 5. Ver logs

```bash
docker logs -f vms_mediamtx_mvp
docker logs -f vms_nginx_mvp
docker logs -f vms_ffmpeg_test
```

## Estrutura de arquivos

```
vms/
├── docker-compose.yml
├── src/
│   ├── frontend/
│   │   └── index.html                    # Player HLS minimalista
│   └── infrastructure/
│       ├── nginx/
│       │   └── nginx.conf                # Reverse proxy config
│       ├── servers/
│       │   └── mediamtx.yml              # MediaMTX config
│       └── test/
│           └── streams/
│               ├── README.md
│               ├── test.html             # Teste 3 streams simultâneos
│               ├── add_cameras.bat       # Adicionar câmeras manualmente
│               └── add_cameras.sh
```

## Configurações importantes

### MediaMTX (mediamtx.yml)

- **HLS Low Latency**: `hlsVariant: fmp4`, `hlsSegmentDuration: 4s`
- **API aberta**: Qualquer usuário pode adicionar câmeras via API
- **Paths dinâmicos**: Câmeras não são pré-configuradas, são adicionadas via API

### NGINX (nginx.conf)

- **Frontend**: Serve `index.html` na raiz
- **Proxy HLS**: `/hls/*` → `mediamtx:8888`
- **CORS**: Headers configurados para permitir acesso cross-origin

### Frontend (index.html)

- **HLS.js**: Player com `lowLatencyMode: true`
- **Minimalista**: Input + botão + video player
- **Destroy on stop**: Player é destruído ao parar stream

## API MediaMTX

### Adicionar câmera

```bash
curl -X POST http://localhost:9997/v3/config/paths/add/NOME_CAMERA \
  -H "Content-Type: application/json" \
  -d '{
    "source": "rtsp://usuario:senha@ip:porta/path",
    "sourceOnDemand": false
  }'
```

### Listar câmeras

```bash
curl http://localhost:9997/v3/paths/list
```

### Remover câmera

```bash
curl -X POST http://localhost:9997/v3/config/paths/remove/NOME_CAMERA
```

## Teste com câmeras reais

### Câmeras de teste configuradas

1. **RTSP Intelbras**
   - URL: `rtsp://admin:Camerite123@45.236.226.71:6047/cam/realmonitor?channel=1&subtype=0`
   - Path: `camera_rtsp`

2. **RTMP SRS**
   - URL: `rtmp://inst-t4ntf-srs-rtmp-intelbras.camerite.services:1935/record/7KOM2715717FV.stream`
   - Path: `camera_rtmp`

3. **IP Camera**
   - URL: `rtsp://138.255.75.231:503`
   - Path: `camera_ip`

## Troubleshooting

### Stream não carrega

1. Verificar se câmera está ativa:
   ```bash
   curl http://localhost:9997/v3/paths/list
   ```

2. Ver logs do MediaMTX:
   ```bash
   docker logs -f vms_mediamtx_mvp
   ```

3. Testar conexão direta com câmera:
   ```bash
   ffmpeg -i "rtsp://camera-url" -t 5 -f null -
   ```

### Erro 404 no HLS

- Câmera não foi adicionada via API
- Fonte RTSP/RTMP não está acessível
- MediaMTX não conseguiu conectar na câmera

### Container não sobe

```bash
docker-compose down
docker rm -f vms_mediamtx_mvp vms_nginx_mvp vms_ffmpeg_test
docker-compose up -d
```

## Próximos passos (Fase 2)

- [ ] Django Admin (CRUD de câmeras)
- [ ] FastAPI Streaming Service
- [ ] Redis (cache)
- [ ] PostgreSQL (persistência)
- [ ] Multi-tenancy (prefeituras)

## Checklist Fase 1 ✅

- [x] docker-compose.yml
- [x] NGINX como reverse proxy
- [x] MediaMTX funcionando
- [x] HLS abrindo no browser
- [x] Câmeras adicionadas via API
- [x] Teste com 3 streams reais
- [x] Documentação completa
