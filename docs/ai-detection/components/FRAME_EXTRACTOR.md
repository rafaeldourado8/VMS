# Frame Extractor

## 📝 O que é

Componente responsável por extrair frames do stream WebRTC do MediaMTX com controle de FPS.

## 🎯 Função

Captura frames de vídeo do canal WebRTC dedicado à IA, aplicando throttling para processar apenas 1-3 FPS (vs 30 FPS original).

## 📊 Input/Output

**Input**: 
- WebRTC stream do MediaMTX (baixa latência)
- URL: `webrtc://mediamtx:8889/camera_{id}_ai`

**Output**:
- Frames RGB (numpy array)
- Taxa: 1-3 FPS configurável
- Formato: (height, width, 3)

## 🔧 Como Funciona

### 1. Conexão WebRTC
```python
# Conecta ao canal IA do MediaMTX
# Canal separado do HLS (usuários)
# Baixa latência (<500ms vs 10-30s HLS)
```

### 2. FPS Throttling
```python
# Captura frame a cada N segundos
# 1 FPS = 1 frame/segundo
# 3 FPS = 3 frames/segundo
# Economia: 90% vs 30 FPS
```

### 3. Reconexão Automática
```python
# Se conexão cair:
#   - Aguarda 5 segundos
#   - Tenta reconectar
#   - Log de erro
#   - Retry infinito
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# FPS para processamento IA
AI_FPS=3

# URL do MediaMTX
MEDIAMTX_URL=http://mediamtx:8889

# Timeout de reconexão (segundos)
RECONNECT_TIMEOUT=5
```

### Exemplo de Uso

```python
from pipeline.frame_extractor import FrameExtractor

extractor = FrameExtractor(
    camera_id=1,
    fps=3,
    mediamtx_url="http://mediamtx:8889"
)

# Inicia captura
extractor.start()

# Obtém frame
frame = extractor.get_frame()

# Para captura
extractor.stop()
```

## 📈 Performance

### Economia de Recursos

| FPS | Frames/min | CPU | Economia |
|-----|------------|-----|----------|
| 30 (original) | 1800 | 100% | - |
| 10 | 600 | 33% | 67% |
| 3 | 180 | 10% | 90% |
| 1 | 60 | 3% | 97% |

**Recomendado**: 3 FPS (balanço entre precisão e custo)

### Latência

- **WebRTC**: <500ms
- **HLS**: 10-30 segundos
- **Ganho**: 20-60x mais rápido

## 🔍 Por que WebRTC?

### vs RTSP Direto
- ✅ Menor latência (500ms vs 2-5s)
- ✅ Melhor controle de FPS
- ✅ Menos banda (já transcoded)
- ✅ Integração com MediaMTX

### vs HLS
- ✅ 20-60x mais rápido
- ✅ Tempo real para IA
- ✅ Canal separado (não afeta usuários)

## ⚠️ Considerações

### Limitações
- Requer MediaMTX configurado para WebRTC
- Necessita canal separado por câmera
- Latência depende da rede local

### Troubleshooting

**Problema**: Frames não chegam
```bash
# Verificar MediaMTX
curl http://mediamtx:8889/v3/paths/list

# Verificar canal IA existe
# Deve ter: camera_1_ai, camera_2_ai, etc
```

**Problema**: Alta latência
```bash
# Verificar rede local
ping mediamtx

# Verificar CPU do MediaMTX
docker stats mediamtx
```

**Problema**: Reconexão constante
```bash
# Verificar logs do MediaMTX
docker logs mediamtx

# Verificar URL da câmera
# RTSP deve estar acessível
```

## 🔗 Relacionado

- [Frame Buffer](./FRAME_BUFFER.md) - Próximo componente
- [MediaMTX Config](../../streaming/STREAMING.md) - Configuração do streaming
- [Pipeline Overview](../README.md#pipeline-de-processamento) - Visão geral
