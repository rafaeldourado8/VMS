# 🎥 Streaming - Arquitetura

## Visão Geral

Sistema de streaming de vídeo baseado em MediaMTX com suporte a múltiplos protocolos e otimizações de performance.

## Componentes

### MediaMTX
- **Versão:** Latest
- **Função:** Servidor de streaming central
- **Protocolos suportados:**
  - RTSP (entrada)
  - HLS (saída para web)
  - WebRTC (futuro)

### Fluxo de Dados

```
Câmera RTSP → MediaMTX → HLS → Frontend
                ↓
           Gravação contínua
```

## Configuração

### MediaMTX Config
```yaml
paths:
  cam_{id}:
    source: rtsp://camera_url
    runOnReady: recording_service
    runOnDemand: true
```

### Características

1. **On-Demand Streaming**
   - Stream só inicia quando há cliente conectado
   - Economiza recursos quando não há visualização
   - Timeout automático após inatividade

2. **HLS Segmentado**
   - Segmentos de 2-4 segundos
   - Buffer mínimo para baixa latência
   - Formato: `.m3u8` + `.mp4` segments

3. **Qualidade Adaptativa**
   - Resolução ajustável por câmera
   - Bitrate otimizado
   - Compressão H.264

## Endpoints

### API de Streaming

```typescript
// Frontend service
streamingService.getHlsUrl(cameraId: number): string
// Retorna: http://mediamtx:8888/cam_{id}/index.m3u8
```

### Health Check
```bash
curl http://mediamtx:8888/v3/config/paths/list
```

## Performance

### Métricas
- Latência: ~2-4 segundos (HLS)
- Banda por stream: ~500KB/s - 2MB/s
- Concurrent streams: Limitado por hardware

### Otimizações Aplicadas
1. Buffer reduzido (5s max)
2. Segmentos curtos (2s)
3. On-demand activation
4. Auto-cleanup de streams inativos

## Troubleshooting

### Stream não inicia
- Verificar URL RTSP da câmera
- Checar conectividade de rede
- Validar credenciais RTSP

### Timeout constante
- Câmera offline ou inacessível
- URL RTSP incorreta
- Firewall bloqueando conexão

### Alta latência
- Aumentar buffer no HLS config
- Verificar banda disponível
- Reduzir qualidade do stream

## Próximos Passos

- [ ] Implementar WebRTC para latência ultra-baixa
- [ ] Adicionar transcodificação adaptativa
- [ ] Suporte a múltiplas qualidades simultâneas
- [ ] Clustering de MediaMTX para alta disponibilidade

---

**Ver também:**
- [Thumbnails](./THUMBNAILS.md)
- [Recording](./RECORDING.md)
- [Protocols](./PROTOCOLS.md)
