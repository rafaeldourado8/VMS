# Sistema LPR Otimizado

## 🎯 Pipeline

```
Input → Detecção Movimento → ROI Automático → YOLO → Tracking → OCR → Output
```

## ✨ Melhorias Implementadas

### 1. **ROI Automático**
- Detecta região de interesse baseado em movimento
- Atualiza a cada 30 frames
- Reduz área de processamento em ~70%

### 2. **Detecção de Movimento**
- Background Subtractor (MOG2)
- Filtra ruído com morfologia
- Identifica apenas áreas com atividade

### 3. **Tracking de Placas**
- ID único por posição (grid 50x50px)
- Evita salvar mesma placa múltiplas vezes
- Aguarda 10 frames de estabilidade antes de salvar
- Limpa tracking após 60 frames

### 4. **OCR Melhorado (EasyOCR)**
- Pré-processamento: resize 2x, blur, threshold adaptativo
- Confiança mínima: 0.5
- Valida texto mínimo: 5 caracteres
- **Só salva se extrair texto com sucesso**

### 5. **Redução de Snapshots**
- Antes: ~1550 snapshots (todos sem texto)
- Agora: Apenas placas com texto extraído
- Redução estimada: **95%**

## 📊 Fluxo de Decisão

```
Frame → ROI? → Movimento? → YOLO Detecta? → Placa Nova? → Estável? → OCR OK? → SALVA
  ↓       ↓         ↓            ↓              ↓            ↓          ↓
 Sim     Sim       Sim          Sim            Sim          Sim        Sim  ✅
 Não     Não       Não          Não            Não          Não        Não  ❌
```

## 🔧 Configuração

### Instalar EasyOCR
```bash
docker-compose exec lpr_service pip install easyocr
```

### Rebuild Container
```bash
docker-compose build lpr_service
docker-compose up -d lpr_service
```

## 📁 Estrutura de Saída

```
snapshots/cam_XXX/TIMESTAMP_UUID/
├── plate.jpg        # Recorte da placa
├── full_frame.jpg   # Frame completo
└── metadata.json    # Com plate_text preenchido
```

### Exemplo metadata.json
```json
{
  "uuid": "a1b2c3d4",
  "camera_id": 999,
  "timestamp": "2026-01-29T04:00:00.000000",
  "plate_text": "ABC1234",
  "confidence": 0.87,
  "bbox": [100, 200, 150, 220],
  "plate_id": "2_4"
}
```

## 🎛️ Parâmetros Ajustáveis

```python
# ROI
history=500              # Histórico background
varThreshold=16          # Sensibilidade movimento
margin=0.2               # Expansão ROI (20%)

# Tracking
stability_frames=10      # Frames para considerar estável
cleanup_frames=60        # Frames para limpar tracking
grid_size=50             # Tamanho grid para ID

# OCR
min_confidence=0.5       # Confiança mínima
min_text_length=5        # Tamanho mínimo texto
resize_factor=2          # Fator upscale
```

## 📈 Performance Esperada

| Métrica | Antes | Depois |
|---------|-------|--------|
| Snapshots/min | ~50 | ~2-5 |
| Taxa sucesso OCR | 0% | 60-80% |
| CPU usage | 100% | 40-60% |
| Duplicatas | Muitas | Zero |

## 🧪 Teste

```bash
# Limpar snapshots antigos
docker-compose exec lpr_service rm -rf /app/snapshots/*

# Reiniciar serviço
docker-compose restart lpr_service

# Aguardar 20s e publicar câmera
timeout /t 20 /nobreak
docker-compose exec lpr_service python -c "import redis,json;r=redis.Redis(host='redis_cache',port=6379,db=2);r.publish('camera:provisioned',json.dumps({'camera_id':100,'rtsp_url':'/app/test_video.mp4'}))"

# Aguardar 60s
timeout /t 60 /nobreak

# Verificar resultados
docker-compose exec lpr_service find /app/snapshots -name "*.json" -exec cat {} \;
```

## 🎯 Resultado Esperado

- Apenas 5-10 snapshots por minuto
- Todos com `plate_text` preenchido
- Sem duplicatas
- Placas estáveis e legíveis
