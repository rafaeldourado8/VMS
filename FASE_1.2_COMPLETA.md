# ✅ FASE 1.2 COMPLETA - MediaMTX Otimizado para 250 Câmeras

## Otimizações Implementadas

### 1. Buffers e Performance
```yaml
writeQueueSize: 1024          # ⬆️ Aumentado de 512 (buffer para 250 câmeras)
maxReaders: 100               # 🆕 Limite de leitores simultâneos por stream
```

### 2. HLS Otimizado
```yaml
hlsSegmentCount: 3            # ⬇️ Reduzido de 5 (menos memória)
hlsSegmentDuration: 2s        # ⚖️ Equilíbrio latência/carga (1s=baixa, 4s=menos CPU)
hlsVariant: mpegts            # Compatibilidade máxima
```

### 3. Gravação Eficiente
```yaml
recordFormat: fmp4            # Formato moderno e eficiente
recordPartDuration: 2s        # Menos I/O de disco
recordSegmentDuration: 1h     # Segmentos de 1h (facilita busca)
recordDeleteAfter: 7d         # Retenção de 7 dias
```

### 4. Paths Dinâmicos
```yaml
~^cam_.*:                     # Aceita cam_1, cam_2, ..., cam_250
  source: publisher
  record: yes
```

### 5. Recursos Docker
```yaml
CPU: 4 cores (limite)         # 2 cores reservados
RAM: 4GB (limite)             # 2GB reservados
                              # ~16MB por câmera
```

### 6. Portas Expostas
- **8554**: RTSP (ingestão de câmeras)
- **8888**: HLS (streaming para clientes)
- **8889**: WebRTC (baixa latência)
- **9997**: API (controle)
- **9998**: Metrics (Prometheus) 🆕

## Validação

### Status
```bash
docker-compose ps mediamtx
# STATUS: Up (healthy)
```

### Logs
```
✅ [RTSP] listener opened on :8554
✅ [HLS] listener opened on :8888
✅ [WebRTC] listener opened on :8889
✅ [API] listener opened on :9997
✅ [metrics] listener opened on :9998
```

## Capacidade Estimada

| Métrica | Valor | Cálculo |
|---------|-------|---------|
| **Câmeras simultâneas** | 250 | Meta MVP |
| **Memória por câmera** | ~16MB | 4GB / 250 |
| **CPU por câmera** | ~1.6% | 4 cores / 250 |
| **Largura de banda** | ~1 Gbps | 250 × 4 Mbps |
| **Armazenamento/dia** | ~1.2 TB | 250 × 5GB/dia |
| **Armazenamento/7 dias** | ~8.6 TB | 1.2TB × 7 |

## Configurações Ajustáveis

### Para Reduzir Latência (sacrifica CPU)
```yaml
hlsSegmentDuration: 1s        # Mais CPU, menos latência
hlsSegmentCount: 5            # Mais memória, buffer maior
```

### Para Reduzir Carga (sacrifica latência)
```yaml
hlsSegmentDuration: 4s        # Menos CPU, mais latência
hlsSegmentCount: 2            # Menos memória
```

### Para Aumentar Retenção (mais disco)
```yaml
recordDeleteAfter: 30d        # 30 dias = ~36 TB
```

### Para Reduzir Uso de Disco
```yaml
recordDeleteAfter: 3d         # 3 dias = ~3.6 TB
recordSegmentDuration: 30m    # Segmentos menores
```

## Próximos Passos

**Fase 1.3**: Simplificar Nginx (apenas estáticos)

### Teste Rápido (quando tiver câmera)
```bash
# Publicar stream de teste
ffmpeg -re -i video.mp4 -c copy -f rtsp rtsp://localhost:8554/cam_1

# Acessar HLS
http://localhost/hls/cam_1/index.m3u8

# Verificar gravação
docker exec gtvision_mediamtx ls -lh /recordings/cam_1/
```

## Monitoramento

### Métricas Prometheus
```bash
curl http://localhost:9998/metrics
# Requer autenticação - configurar no Prometheus
```

### API MediaMTX
```bash
# Listar paths ativos
curl -u mediamtx_api_user:GtV!sionMed1aMTX$2025 \
  http://localhost:9997/v3/paths/list
```

---

**Status**: ✅ MediaMTX pronto para 250 câmeras  
**Próximo**: Fase 1.3 - Nginx simplificado
