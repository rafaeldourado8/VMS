# COMMIT - PASSO 6: Mosaicos e HLS Player

## Resumo
Implementado sistema de mosaicos (até 4 streams) e player HLS minimalista para consumo de vídeo. URLs estáveis por câmera, suporte a RTSP/RTMP/IP/P2P, HLS sob demanda.

## Arquivos Criados
- `src/shared/streaming/mosaicos/models.py` - Dataclass Mosaic
- `src/shared/streaming/mosaicos/mosaic_manager.py` - Interface
- `src/infrastructure/cache/streaming/redis_mosaic_manager.py` - Implementação Redis
- `src/shared/streaming/mosaicos/mosaic_endpoints.py` - Endpoints FastAPI
- `frontend/player.html` - Player HLS com métricas
- `test_hls.bat` - Script teste RTMP
- `test_rtsp.bat` - Script teste RTSP
- `test_mosaic.bat` - Script teste mosaico
- `add_to_mosaic.bat` - Script adicionar streams
- `open_player.bat` - Abrir player
- `docs/streaming/PASSO6.md` - Documentação

## Arquivos Modificados
- `src/shared/streaming/stream/api.py` - Integrou mosaic_manager e endpoints
- `src/infrastructure/nginx/nginx.conf` - Proxy /hls/* e try_files corrigido
- `docker-compose.yml` - Volume frontend montado
- `src/infrastructure/servers/mediamtx.yml` - hlsAlwaysRemux: no

## Funcionalidades
- ✅ Criar mosaico (max 4 streams)
- ✅ Adicionar/remover streams
- ✅ TTL 2 horas Redis
- ✅ Player HLS low-latency
- ✅ Métricas tempo real (qualidade, buffer, latência)
- ✅ URLs estáveis: /hls/stream_{camera_id}/index.m3u8
- ✅ Suporte RTSP, RTMP, IP, P2P
- ✅ HLS sob demanda (economiza recursos)

## Testes
- ✅ 4 streams RTMP simultâneos
- ✅ Mosaico com 4 streams
- ✅ HLS via NGINX funcionando
- ✅ Player reproduzindo com métricas

## Próximo Passo
PASSO 7 - Gravação Cíclica (record → sobrescreve → limpa)
