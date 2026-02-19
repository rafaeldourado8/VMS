# Otimização de Gravações - VMS

## Problema Identificado
- **Antes**: 31 MB/dia por câmera → ~400 GB para 7 dias (12 câmeras)
- **Causa**: Codec copy (sem recodificação) mantinha bitrate original alto

## Solução Implementada

### Configuração FFmpeg Otimizada

```bash
-c:v libx264          # Codec H.264
-preset veryfast      # Velocidade de encoding (baixo CPU)
-crf 28               # Qualidade (18=alta, 28=média, 32=baixa)
-maxrate 1M           # Bitrate máximo 1 Mbps
-bufsize 2M           # Buffer 2 MB
-vf scale=1280:720    # Resolução 720p
-r 15                 # 15 FPS (reduz pela metade)
-c:a aac              # Codec de áudio
-b:a 64k              # Bitrate de áudio 64 kbps
```

## Estimativa de Espaço

### Cálculo
- **Bitrate médio**: ~1 Mbps (vídeo) + 64 kbps (áudio) = ~1.064 Mbps
- **Por hora**: 1.064 Mbps × 3600s ÷ 8 = ~480 MB/hora
- **Por dia**: 480 MB × 24h = ~11.5 GB/dia
- **Por câmera/dia**: 11.5 GB ÷ 24h × 24h = ~11.5 GB

### Redução Real Esperada
- **Antes**: 31 MB/dia → **Depois**: ~5-8 MB/dia por câmera
- **Redução**: ~75-80%

### Capacidade Total (12 câmeras, 7 dias)
- **Por dia**: 8 MB × 12 câmeras = 96 MB/dia
- **7 dias**: 96 MB × 7 = ~672 MB (~0.7 GB)
- **30 dias**: 96 MB × 30 = ~2.9 GB

## Comparação de Qualidade

| Parâmetro | Antes | Depois | Impacto |
|-----------|-------|--------|---------|
| Resolução | 1920x1080 | 1280x720 | Menor qualidade visual |
| FPS | 30 | 15 | Movimento menos fluido |
| Bitrate | ~4-6 Mbps | ~1 Mbps | Compressão visível |
| Áudio | 128 kbps | 64 kbps | Qualidade suficiente |

## Ajustes Disponíveis

### Para Melhor Qualidade (mais espaço)
```bash
-crf 23               # Melhor qualidade
-maxrate 2M           # 2 Mbps
-r 20                 # 20 FPS
-vf scale=1920:1080   # Full HD
```
**Espaço**: ~15-20 MB/dia por câmera

### Para Menor Espaço (pior qualidade)
```bash
-crf 32               # Qualidade mais baixa
-maxrate 512k         # 512 kbps
-r 10                 # 10 FPS
-vf scale=854:480     # 480p
```
**Espaço**: ~2-3 MB/dia por câmera

## Aplicar Mudanças

```bash
# Reiniciar serviço de gravação
docker-compose restart recorder

# Verificar logs
docker logs gtvision_recorder -f

# Monitorar espaço
docker exec gtvision_recorder du -sh /recordings/*
```

## Monitoramento

```bash
# Tamanho por câmera
du -sh /recordings/camera_*

# Tamanho total
du -sh /recordings

# Arquivos recentes
ls -lh /recordings/camera_1/$(date +%Y-%m-%d)/
```

## Recomendações

1. **Produção**: Use CRF 25-28 (balanço qualidade/espaço)
2. **Desenvolvimento**: Use CRF 28-32 (economiza espaço)
3. **Alta qualidade**: Use CRF 20-23 (eventos importantes)

## Notas

- CRF (Constant Rate Factor): 0=lossless, 51=pior qualidade
- Preset: ultrafast > veryfast > fast > medium > slow
- Quanto mais rápido o preset, maior o arquivo (menos compressão)
