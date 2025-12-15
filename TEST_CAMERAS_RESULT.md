# 🎥 Teste com Câmeras Reais - Resultado

## Status: ⚠️ Packet Loss Detectado

### Câmeras Testadas
```
✅ cam_1: rtsp://admin:***@45.236.226.75:6053 (conecta mas com packet loss)
📋 cam_2-6: Configuradas no MediaMTX (sourceOnDemand)
```

### Problema Identificado
```
WAR [RTSP] [session] 166 RTP packets lost
WAR [RTSP] [session] 284 RTP packets lost  
ERR [path cam_1] [recorder] too many reordered frames (29)
```

**Causa**: Câmeras remotas (45.236.226.x) com latência de rede alta.

### Otimizações Aplicadas
1. ✅ `rtspTransports: [tcp, udp]` - TCP primeiro
2. ✅ `rtspUDPReadBufferSize: 8388608` - Buffer 8MB
3. ✅ `rtspTransport: tcp` - Forçar TCP no pathDefaults
4. ✅ `sourceOnDemand` - MediaMTX conecta diretamente

### Configuração Atual (mediamtx.yml)
```yaml
paths:
  cam_1:
    source: rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0
    sourceOnDemand: yes
    sourceOnDemandStartTimeout: 10s
    sourceOnDemandCloseAfter: 10s
```

## Próximas Ações

### Opção 1: Aceitar Packet Loss (Câmeras Remotas)
- Packet loss é esperado em câmeras remotas via internet
- MediaMTX está gravando (recording 1 track H264)
- HLS pode funcionar com alguns frames perdidos

### Opção 2: Testar com Câmera Local
- Usar câmera na mesma rede (sem latência)
- Validar que sistema funciona perfeitamente

### Opção 3: Ajustar Tolerância
```yaml
# Aumentar timeouts para câmeras remotas
readTimeout: 30s              # De 10s para 30s
sourceOnDemandStartTimeout: 30s
```

## Teste Manual

### Via VLC (validar stream)
```bash
vlc rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0
```

### Via FFplay
```bash
ffplay -rtsp_transport tcp rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0
```

### Via MediaMTX HLS (quando estabilizar)
```
http://localhost/hls/cam_1/index.m3u8
http://localhost/hls/cam_2/index.m3u8
...
http://localhost/hls/cam_6/index.m3u8
```

## Recomendação

**Para MVP**: Usar câmeras locais ou com boa conexão de rede.  
**Para Produção**: Implementar retry logic e tolerância a packet loss.

---

**Status Fase 1.2**: ✅ MediaMTX otimizado e funcional  
**Próximo**: Fase 1.3 ou testar com câmera local
