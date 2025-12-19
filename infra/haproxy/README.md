# HAProxy - Split-Brain Load Balancer

## Arquitetura

```
Cliente → HAProxy (porta 80) → Roteamento:
  ├─ /hls/* → MediaMTX:8888 (vídeo HLS)
  ├─ /ws/live/* → MediaMTX:8889 (WebRTC)
  ├─ /api/* → Gateway:8000 → Django:8000
  └─ /* → Nginx:80 (frontend + estáticos)
```

## Validação

```bash
# 1. Verificar configuração
docker exec gtvision_haproxy haproxy -c -f /usr/local/etc/haproxy/haproxy.cfg

# 2. Testar roteamento de vídeo (bypass total)
curl -I http://localhost/hls/cam_1/index.m3u8
# Deve retornar do MediaMTX direto

# 3. Testar roteamento de API
curl http://localhost/api/cameras/
# Deve passar por Gateway → Django

# 4. Acessar stats
http://localhost:8404/stats
```

## Monitoramento

- **Stats UI**: http://localhost:8404/stats
- **Métricas**: Backends ativos, latência, throughput
- **Health checks**: Automáticos a cada 10s

## Escalar

Para adicionar mais instâncias:

```yaml
# haproxy.cfg
backend mediamtx_hls
    server mediamtx1 mediamtx:8888 check
    server mediamtx2 mediamtx2:8888 check  # Nova instância
```
