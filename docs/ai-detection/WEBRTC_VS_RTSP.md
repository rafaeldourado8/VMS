# WebRTC vs RTSP - AI Detection

## 🎯 Visão Geral

O AI Detection Service suporta **dois modos de captura**:
1. **WebRTC** (Recomendado) - Baixa latência, via MediaMTX WHEP
2. **RTSP** (Fallback) - Compatibilidade universal

## 📊 Comparação

| Feature | WebRTC | RTSP |
|---------|--------|------|
| **Latência** | <500ms | 2-5s |
| **Protocolo** | HTTP/WHEP | RTSP |
| **Porta** | 8889 | 8554 |
| **Overhead** | Baixo | Médio |
| **Compatibilidade** | Requer GStreamer | Universal |
| **Streaming HLS** | ✅ Não interfere | ✅ Não interfere |

## 🔧 Como Funciona

### WebRTC (WHEP)
```
Camera RTSP → MediaMTX → [WebRTC WHEP] → AI Detection
                       └→ [HLS] → Usuários (não afetado)
```

**Características**:
- MediaMTX expõe endpoint WHEP: `http://mediamtx:8889/camera_{id}/whep`
- AI Detection faz request HTTP para obter stream WebRTC
- **Zero impacto** no streaming HLS existente
- Múltiplos consumidores do mesmo stream

### RTSP (Fallback)
```
Camera RTSP → MediaMTX → [RTSP] → AI Detection
                       └→ [HLS] → Usuários (não afetado)
```

**Características**:
- MediaMTX expõe RTSP: `rtsp://mediamtx:8554/camera_{id}`
- AI Detection conecta via OpenCV VideoCapture
- **Zero impacto** no streaming HLS existente

## ⚙️ Configuração

### Habilitar WebRTC (Padrão)
```bash
USE_WEBRTC=true
MEDIAMTX_WEBRTC_URL=http://mediamtx:8889
```

### Desabilitar WebRTC (Usar RTSP)
```bash
USE_WEBRTC=false
MEDIAMTX_URL=http://mediamtx:9997
```

## 🚀 Iniciar Câmera

### Modo Automático (Recomendado)
```bash
# AI Detection busca automaticamente do MediaMTX
curl -X POST http://localhost:5000/camera/start \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 1}'
```

**O que acontece**:
1. AI Detection consulta MediaMTX API
2. Se `USE_WEBRTC=true`: usa `http://mediamtx:8889/camera_1/whep`
3. Se `USE_WEBRTC=false`: usa `rtsp://mediamtx:8554/camera_1`
4. Streaming HLS continua funcionando normalmente

### Modo Manual (URL Customizada)
```bash
# Fornecer URL RTSP diretamente
curl -X POST http://localhost:5000/camera/start \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 1,
    "source_url": "rtsp://admin:pass@192.168.1.100:554/stream"
  }'
```

## 🔍 Verificar Modo Ativo

```bash
# Ver logs
docker logs ai_detection | grep "WebRTC enabled"

# Output esperado:
# WebRTC enabled: True
# Using WebRTC for camera 1: http://mediamtx:8889/camera_1/whep
```

## 📈 Performance

### WebRTC
- **Latência**: 200-500ms
- **CPU**: +5% (decodificação)
- **Banda**: Mesma do RTSP
- **Precisão**: Mesma do RTSP

### RTSP
- **Latência**: 2-5s
- **CPU**: Baseline
- **Banda**: Mesma do WebRTC
- **Precisão**: Mesma do WebRTC

## ⚠️ Troubleshooting

### WebRTC não conecta
```bash
# 1. Verificar GStreamer instalado
docker exec ai_detection gst-launch-1.0 --version

# 2. Testar endpoint WHEP
curl http://mediamtx:8889/camera_1/whep

# 3. Fallback para RTSP
USE_WEBRTC=false
```

### RTSP não conecta
```bash
# 1. Verificar MediaMTX RTSP
ffmpeg -i rtsp://mediamtx:8554/camera_1 -frames:v 1 test.jpg

# 2. Verificar path existe
curl http://mediamtx:9997/v3/paths/get/camera_1
```

### Streaming HLS afetado?
**NÃO!** O AI Detection é apenas mais um **consumidor** do MediaMTX.

```
Camera RTSP → MediaMTX
                ├─ Consumer 1: HLS (Usuários) ✅
                ├─ Consumer 2: WebRTC (AI Detection) ✅
                └─ Consumer 3: RTSP (Gravação) ✅
```

Todos os consumidores são **independentes** e **não interferem** entre si.

## 🎯 Recomendações

### Produção
```bash
USE_WEBRTC=true  # Menor latência
AI_FPS=3         # Balanço
```

### Desenvolvimento
```bash
USE_WEBRTC=true  # Testar WebRTC
AI_FPS=5         # Mais frames
```

### Troubleshooting
```bash
USE_WEBRTC=false # RTSP mais estável
AI_FPS=1         # Menos carga
```

## 📚 Referências

- [MediaMTX WHEP](https://github.com/bluenviron/mediamtx#whep)
- [GStreamer WebRTC](https://gstreamer.freedesktop.org/documentation/webrtc/index.html)
- [OpenCV VideoCapture](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html)
