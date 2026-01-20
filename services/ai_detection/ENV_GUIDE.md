# 🔧 Variáveis de Ambiente - AI Detection

## 📋 Todas as Variáveis

### MediaMTX
```bash
MEDIAMTX_URL=http://mediamtx:9997          # API do MediaMTX
MEDIAMTX_WEBRTC_URL=http://mediamtx:8889   # WebRTC endpoint
USE_WEBRTC=true                             # Usar WebRTC (vs RTSP)
```

### Frame Processing
```bash
AI_FPS=3                                    # FPS para processar (1-5)
```

### Motion Detection
```bash
MOTION_THRESHOLD=0.03                       # Threshold movimento (0.01-0.10)
MOG2_VAR_THRESHOLD=16                       # Sensibilidade MOG2 (8-32)
MOG2_HISTORY=500                            # Frames histórico (100-1000)
```

### Vehicle Detection
```bash
VEHICLE_CONFIDENCE=0.5                      # Confiança veículos (0.3-0.7)
VEHICLE_MODEL=models/vehicle_yolov8n.pt     # Modelo YOLO veículos
```

### Tracking
```bash
TRACKER_IOU_THRESHOLD=0.3                   # IoU threshold (0.2-0.5)
TRACKER_TIMEOUT=5                           # Timeout em segundos (3-10)
```

### Quality Scoring
```bash
QUALITY_WEIGHT_BLUR=0.35                    # Peso blur (0-1)
QUALITY_WEIGHT_ANGLE=0.30                   # Peso ângulo (0-1)
QUALITY_WEIGHT_CONTRAST=0.20                # Peso contraste (0-1)
QUALITY_WEIGHT_SIZE=0.15                    # Peso tamanho (0-1)
MIN_QUALITY_SCORE=50                        # Score mínimo (0-100)
```

### Plate Detection
```bash
PLATE_CONFIDENCE=0.6                        # Confiança placas (0.5-0.8)
PLATE_MODEL=models/plate_yolov8n.pt         # Modelo YOLO placas (FINE-TUNED)
```

### OCR
```bash
OCR_MODEL=cct-xs-v1-global-model            # Modelo Fast-Plate-OCR
```

### Consensus
```bash
MIN_READINGS=3                              # Mínimo leituras (3-7)
MAX_READINGS=5                              # Máximo leituras (5-10)
CONSENSUS_THRESHOLD=0.6                     # Threshold consenso (0.5-0.8)
SIMILARITY_THRESHOLD=0.8                    # Threshold similaridade (0.7-0.9)
MIN_CONFIDENCE=0.75                         # Confiança mínima (0.7-0.9)
```

### Deduplication
```bash
REDIS_HOST=redis_cache                      # Host Redis
REDIS_PORT=6379                             # Porta Redis
DEDUP_TTL=300                               # TTL cache (segundos)
```

### Backend
```bash
BACKEND_URL=http://backend:8000             # URL Backend
RABBITMQ_HOST=rabbitmq                      # Host RabbitMQ
RABBITMQ_PORT=5672                          # Porta RabbitMQ
RABBITMQ_USER=vms                           # User RabbitMQ
RABBITMQ_PASS=vms123                        # Pass RabbitMQ
```

### API
```bash
API_PORT=5000                               # Porta Flask API
LOG_LEVEL=INFO                              # Nível log (DEBUG/INFO/WARNING)
```

## 🎯 Perfis Recomendados

### Produção (Balanço)
```bash
USE_WEBRTC=true
AI_FPS=3
MOTION_THRESHOLD=0.03
MIN_READINGS=5
CONSENSUS_THRESHOLD=0.6
MIN_CONFIDENCE=0.75
```

### Alta Performance (Custo Mínimo)
```bash
USE_WEBRTC=true
AI_FPS=1
MOTION_THRESHOLD=0.05
MIN_READINGS=3
CONSENSUS_THRESHOLD=0.5
MIN_CONFIDENCE=0.70
```

### Desenvolvimento (Precisão Máxima)
```bash
USE_WEBRTC=true
AI_FPS=5
MOTION_THRESHOLD=0.01
MIN_READINGS=7
CONSENSUS_THRESHOLD=0.7
MIN_CONFIDENCE=0.85
LOG_LEVEL=DEBUG
```

### Teste (Sem WebRTC)
```bash
USE_WEBRTC=false
AI_FPS=1
MOTION_THRESHOLD=0.05
MIN_READINGS=3
```

## 🔧 Ajustes Comuns

### Muitas detecções falsas
```bash
VEHICLE_CONFIDENCE=0.6          # Aumentar
PLATE_CONFIDENCE=0.7            # Aumentar
MIN_CONFIDENCE=0.80             # Aumentar
CONSENSUS_THRESHOLD=0.7         # Aumentar
```

### Poucas detecções
```bash
VEHICLE_CONFIDENCE=0.4          # Diminuir
PLATE_CONFIDENCE=0.5            # Diminuir
MIN_CONFIDENCE=0.70             # Diminuir
MOTION_THRESHOLD=0.01           # Diminuir
```

### Alto uso de CPU
```bash
AI_FPS=1                        # Diminuir
MOTION_THRESHOLD=0.05           # Aumentar (mais frames descartados)
MIN_READINGS=3                  # Diminuir
```

### Baixa precisão
```bash
MIN_READINGS=7                  # Aumentar
CONSENSUS_THRESHOLD=0.7         # Aumentar
MIN_CONFIDENCE=0.85             # Aumentar
QUALITY_WEIGHT_BLUR=0.40        # Aumentar peso blur
```

### Muitas duplicatas
```bash
DEDUP_TTL=600                   # Aumentar (10 min)
SIMILARITY_THRESHOLD=0.7        # Diminuir (mais permissivo)
```

## ⚠️ Importante

1. **Sempre use modelos fine-tuned**: `PLATE_MODEL=models/plate_yolov8n.pt`
2. **WebRTC recomendado**: `USE_WEBRTC=true` (menor latência)
3. **Pesos devem somar 1.0**: blur + angle + contrast + size = 1.0
4. **TTL em segundos**: 300 = 5 minutos

## 🔗 Referências

- [Configuração Completa](./.env.example)
- [Documentação Modelos](./models/README.md)
- [Guia de Deploy](../../docs/ai-detection/DOCKER_DEPLOY.md)
