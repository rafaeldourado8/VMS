# Visualizar Stream com Bounding Boxes

## 🎥 Stream Anotado

O sistema agora publica o vídeo processado com:
- **Bounding boxes coloridas**:
  - 🔴 Vermelho: Placa nova detectada
  - 🟡 Amarelo: Placa em tracking
  - 🟢 Verde: Placa já salva
- **ROI** em azul ciano
- **Labels** com texto da placa e confiança
- **Info** do frame e quantidade de placas tracked

## 📺 Como Visualizar

### 1. Publicar Câmera
```bash
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':300,'rtsp_url':'/app/test_video.mp4'}))"
```

### 2. Assistir Stream Anotado

**URL do Stream:**
```
rtsp://localhost:8554/cam_300_ai
```

**Com VLC:**
```bash
vlc rtsp://localhost:8554/cam_300_ai
```

**Com FFplay:**
```bash
ffplay -rtsp_transport tcp rtsp://localhost:8554/cam_300_ai
```

**No Browser (via HLS):**
```
http://localhost:8888/cam_300_ai
```

## 🎨 Legenda de Cores

| Cor | Status | Significado |
|-----|--------|-------------|
| 🔴 Vermelho | NEW | Placa detectada pela primeira vez |
| 🟡 Amarelo | TRACKING | Placa sendo rastreada (aguardando estabilidade) |
| 🟢 Verde | SAVED | Placa já foi salva (snapshot criado) |
| 🔵 Azul Ciano | ROI | Região de interesse (área com movimento) |

## 📊 Informações no Frame

```
Cam 300 | Frame 1234        ← Câmera e número do frame
Tracked: 5                  ← Quantidade de placas em tracking
```

## 🧪 Teste Completo

```bash
# 1. Limpar snapshots
docker-compose exec lpr_service rm -rf /app/snapshots/*

# 2. Publicar câmera
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':300,'rtsp_url':'/app/test_video.mp4'}))"

# 3. Abrir VLC
vlc rtsp://localhost:8554/cam_300_ai

# 4. Verificar logs
docker-compose logs -f lpr_service
```

## 🎯 O Que Você Verá

1. **Caixas vermelhas** aparecem quando uma placa é detectada
2. Caixas ficam **amarelas** enquanto o sistema aguarda estabilidade (10 frames)
3. Quando salva o snapshot, a caixa fica **verde**
4. O **texto da placa** aparece acima da caixa (se OCR estiver disponível)
5. A **área ROI** em azul mostra onde há movimento

## 🔧 Troubleshooting

**Stream não aparece:**
```bash
# Verificar se MediaMTX está rodando
docker-compose ps mediamtx

# Verificar logs do LPR
docker-compose logs --tail=50 lpr_service | findstr STREAM
```

**Sem bounding boxes:**
```bash
# Verificar se está detectando
docker-compose logs lpr_service | findstr "SAVED\|TRACKING"
```

## 📱 Múltiplas Câmeras

Cada câmera tem seu próprio stream:
- Câmera 100: `rtsp://localhost:8554/cam_100_ai`
- Câmera 200: `rtsp://localhost:8554/cam_200_ai`
- Câmera 300: `rtsp://localhost:8554/cam_300_ai`
