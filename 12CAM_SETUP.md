# 🎥 VMS - Configuração para 12 Câmeras Simultâneas

## 🎯 Objetivo
Sistema otimizado para **12 câmeras simultâneas** mantendo:
- ✅ **Qualidade preservada**
- ✅ **Latência ultra-baixa** (~2-4 segundos)
- ✅ **Zero delay** entre câmeras
- ✅ **Estabilidade de longa duração**

## 📊 Especificações Técnicas

### 🔧 Recursos Alocados
```yaml
MediaMTX:    2.5 CPU, 2GB RAM
Streaming:   1.5 CPU, 1GB RAM  
Nginx:       0.5 CPU, 256MB RAM
Redis:       0.5 CPU, 512MB RAM
----------------------------
Total:       5.0 CPU, 3.8GB RAM
```

### ⚡ Configurações de Latência
```yaml
HLS Segmentos:     2 (mínimo absoluto)
Duração Segmento:  2s (ultra-rápido)
Parte HLS:         0.5s (sub-segundo)
Buffer Player:     3s (mínimo)
Timeout Conexão:   10s (muito rápido)
```

## 🚀 Como Iniciar

### 1. Iniciar Sistema
```bash
start_12cam.bat
```

### 2. Provisionar Câmeras (1-12)
```bash
# Câmera 1
curl -X POST http://localhost:8001/cameras/provision \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 1, "rtsp_url": "rtsp://camera1-ip:554/stream", "name": "Cam1"}'

# Câmera 2
curl -X POST http://localhost:8001/cameras/provision \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 2, "rtsp_url": "rtsp://camera2-ip:554/stream", "name": "Cam2"}'

# ... até câmera 12
```

### 3. Acessar Streams
```
Câmera 1: http://localhost/hls/cam_1/index.m3u8
Câmera 2: http://localhost/hls/cam_2/index.m3u8
...
Câmera 12: http://localhost/hls/cam_12/index.m3u8
```

## 🎮 Player Frontend Otimizado

### Uso do TwelveCamManager
```javascript
// Inicializar gerenciador
const camManager = new TwelveCamManager();

// Adicionar câmeras
for (let i = 1; i <= 12; i++) {
    camManager.addPlayer(
        `camera-${i}`, 
        `http://localhost/hls/cam_${i}/index.m3u8`
    );
}

// Otimizar viewport (pausa câmeras não visíveis)
setInterval(() => {
    camManager.optimizeForViewport();
}, 5000);
```

### Configurações Ultra-Otimizadas
```javascript
{
    maxBufferLength: 3,           // 3s buffer máximo
    liveSyncDurationCount: 1,     // 1 segmento apenas
    backBufferLength: 2,          // 2s buffer traseiro
    lowLatencyMode: true,         // Modo baixa latência
    enableWorker: true            // Web Worker ativo
}
```

## 📈 Monitoramento

### Verificar Status
```bash
# Status geral
curl http://localhost:8001/health

# Estatísticas detalhadas
curl http://localhost:8001/stats

# Uso de recursos
docker stats
```

### Logs Importantes
```bash
# MediaMTX
docker-compose -f docker-compose.12cam.yml logs -f mediamtx

# Streaming Service
docker-compose -f docker-compose.12cam.yml logs -f streaming

# Nginx
docker-compose -f docker-compose.12cam.yml logs -f nginx
```

## 🎯 Otimizações Aplicadas

### 1. MediaMTX
- **Segmentos HLS**: 2 de 2s (4s total)
- **Partes HLS**: 0.5s (sub-segundo)
- **TCP apenas**: Mais estável que UDP
- **Buffer reduzido**: 4MB por stream
- **Sem gravação**: Economia máxima

### 2. Nginx Proxy
- **Cache HLS**: 1s para playlists
- **Gzip ativo**: Economia de banda
- **Keep-alive**: Conexões persistentes
- **Buffer otimizado**: Para 12 streams

### 3. Player Frontend
- **Buffer mínimo**: 3s total
- **Limpeza agressiva**: A cada 10s
- **Viewport optimization**: Pausa não-visíveis
- **Restart rápido**: 500ms

### 4. Streaming Service
- **2 workers**: Paralelismo otimizado
- **Timeouts rápidos**: 10s conexão
- **4 viewers/câmera**: Limite controlado

## 📊 Performance Esperada

### ✅ Latência
- **Primeira visualização**: 2-4 segundos
- **Troca entre câmeras**: <1 segundo
- **Sincronização**: Todas em sync

### ✅ Qualidade
- **Resolução**: Preservada da fonte
- **Bitrate**: Sem recodificação
- **FPS**: Mantido da câmera

### ✅ Recursos
- **CPU**: ~60-80% (4 cores)
- **RAM**: ~4-5GB total
- **Rede**: ~50-100 Mbps (depende das câmeras)

## 🔧 Troubleshooting

### Problema: Alta latência
```bash
# Verificar segmentos HLS
curl http://localhost/hls/cam_1/index.m3u8

# Deve mostrar apenas 2 segmentos
```

### Problema: Câmera não inicia
```bash
# Verificar logs
docker-compose -f docker-compose.12cam.yml logs mediamtx | grep cam_X

# Testar RTSP diretamente
ffplay rtsp://camera-ip:554/stream
```

### Problema: Alto uso de CPU
```bash
# Verificar containers
docker stats

# Reduzir número de câmeras ativas se necessário
```

## 🎯 Limites e Recomendações

### ✅ Recomendado
- **Até 12 câmeras**: Performance otimizada
- **Resolução**: Até 1080p por câmera
- **Bitrate**: 2-4 Mbps por câmera
- **Hardware**: 4+ cores, 8GB+ RAM

### ⚠️ Cuidados
- **Rede estável**: Essencial para 12 streams
- **Câmeras confiáveis**: RTSP estável
- **Monitoramento**: Verificar recursos regularmente

---

**Status**: ✅ Otimizado para 12 câmeras simultâneas  
**Latência**: 2-4 segundos (ultra-baixa)  
**Qualidade**: Preservada sem recodificação  
**Estabilidade**: Testado para operação contínua