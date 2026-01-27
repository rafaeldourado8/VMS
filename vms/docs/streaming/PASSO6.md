# PASSO 6 - Mosaicos e HLS Player

## Objetivo
Implementar sistema de mosaicos (até 4 streams simultâneos) e player HLS para consumo de vídeo.

## Implementação

### 1. Mosaicos
**Arquivos:**
- `src/shared/streaming/mosaicos/models.py` - Dataclass Mosaic (max 4 streams)
- `src/shared/streaming/mosaicos/mosaic_manager.py` - Interface MosaicManager
- `src/infrastructure/cache/streaming/redis_mosaic_manager.py` - Implementação Redis
- `src/shared/streaming/mosaicos/mosaic_endpoints.py` - Endpoints FastAPI

**Funcionalidades:**
- Criar mosaico (user_id + city_id)
- Adicionar/remover streams (máx 4)
- Listar streams do mosaico
- Deletar mosaico
- TTL 2 horas no Redis

**Endpoints:**
```
POST   /api/mosaics/create
GET    /api/mosaics/{mosaic_id}
POST   /api/mosaics/{mosaic_id}/add/{session_id}
DELETE /api/mosaics/{mosaic_id}/remove/{session_id}
DELETE /api/mosaics/{mosaic_id}
```

### 2. HLS Player
**Arquivos:**
- `frontend/player.html` - Player minimalista com HLS.js
- `src/infrastructure/nginx/nginx.conf` - Proxy /hls/* → MediaMTX:8888
- `docker-compose.yml` - Volume frontend montado no NGINX

**Características:**
- HLS.js low-latency mode
- Métricas em tempo real (qualidade, buffer, latência)
- Presets para streams RTMP
- Auto-recovery em erros de rede/mídia
- UI dark minimalista

**Configuração MediaMTX:**
- `hlsAlwaysRemux: no` - HLS sob demanda (economiza recursos)
- `hlsVariant: fmp4` - Low-latency
- `hlsSegmentDuration: 4s` - Segmentos de 4 segundos
- `hlsSegmentCount: 6` - Buffer de 6 segmentos

### 3. URLs Estáveis
**Pattern:** `http://localhost/hls/stream_{camera_id}/index.m3u8`

**Exemplos:**
- RTMP: `http://localhost/hls/stream_d7ebdaac-9d09-470f-a208-34ce2e4f9689/index.m3u8`
- RTSP: `http://localhost/hls/stream_0c4a7f3e-ec5f-4c5e-b5e5-d5e5e5e5e5e5/index.m3u8`

Frontend não sabe nada de MediaMTX, apenas consome via NGINX.

## Protocolos Suportados
- **RTSP** - Câmeras IP tradicionais
- **RTMP** - Streaming servers
- **IP** - HTTP/HTTPS streams
- **P2P** - Protocolo proprietário

Todos convertidos para HLS automaticamente pelo MediaMTX.

## Testes

### Scripts
- `test_hls.bat` - Testa stream RTMP + HLS
- `test_rtsp.bat` - Testa stream RTSP + HLS
- `test_mosaic.bat` - Cria mosaico com 4 streams
- `add_to_mosaic.bat` - Adiciona streams ao mosaico
- `open_player.bat` - Abre player no navegador

### Fluxo Completo Testado
1. Setup ambiente (superuser, cidade, câmeras)
2. Iniciar 4 streams RTMP simultaneamente
3. Verificar paths no MediaMTX (4 ativos)
4. Criar mosaico
5. Adicionar 4 session_ids ao mosaico
6. Abrir player e reproduzir stream

### Resultados
- ✅ 4 streams RTMP iniciados (status 200)
- ✅ 4 paths ativos no MediaMTX
- ✅ Mosaico criado com 4 streams
- ✅ HLS funcionando via NGINX
- ✅ Player reproduzindo com métricas

## Arquitetura

### Fluxo de Dados
```
Câmera (RTSP/RTMP/IP/P2P)
    ↓
MediaMTX (converte → HLS)
    ↓
NGINX (proxy /hls/*)
    ↓
Player (HLS.js)
```

### Isolamento Multi-Tenant
- Mosaicos isolados por city_id
- Sessões isoladas por city_id
- Headers obrigatórios: X-City-ID, X-User-ID

### Redis Keys
- `mosaic:{mosaic_id}` - Dados do mosaico (TTL 2h)
- `city:{city_id}:mosaics` - Set de mosaicos da cidade
- `session:{session_id}` - Dados da sessão (TTL 1h)
- `city:{city_id}:sessions` - Set de sessões da cidade

## Configuração

### NGINX
```nginx
location /hls/ {
    proxy_pass http://mediamtx/;
    proxy_http_version 1.1;
    add_header Access-Control-Allow-Origin *;
    add_header Cache-Control no-cache;
}
```

### Docker Compose
```yaml
nginx:
  volumes:
    - ./frontend:/usr/share/nginx/html:ro
```

## Próximos Passos
- Passo 7: Gravação cíclica (record → sobrescreve → limpa)
- Passo 8+: Player replay, busca, download, eventos LPR, IA
