# 🧪 Teste do LPR Detection Service

## 🚀 Iniciar Serviço

```bash
# Build e start
docker-compose up -d lpr_detection

# Ver logs
docker-compose logs -f lpr_detection
```

## ✅ Verificar Health

```bash
curl http://localhost:5000/health
# Esperado: {"status":"ok"}
```

## 🎥 Testar com Câmeras Reais

### Câmera RTSP (deve processar LPR)
```bash
# Adicionar câmera RTSP no backend
curl -X POST http://localhost:8000/api/cameras/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Camera RTSP LPR",
    "rtsp_url": "rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0",
    "location": "Entrada",
    "status": "online"
  }'

# Verificar logs do LPR
docker-compose logs -f lpr_detection
# Esperado: "Iniciando processamento LPR para câmera RTSP..."
```

### Câmera RTMP (deve pular LPR)
```bash
# Adicionar câmera RTMP no backend
curl -X POST http://localhost:8000/api/cameras/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Camera RTMP Bullet",
    "rtsp_url": "rtmp://inst-czd17-srs-rtmp-hik-pro-connect.camerite.services:1935/record/FC2487237.stream",
    "location": "Estacionamento",
    "status": "online"
  }'

# Verificar logs do LPR
docker-compose logs -f lpr_detection
# Esperado: "Câmera ... é RTMP (bullet), pulando processamento LPR"
```

## 📊 Verificar Detecções

### Banco Local (SQLite)
```bash
docker exec -it gtvision_lpr_detection sqlite3 aiprocessor.db
sqlite> SELECT * FROM vehicle_info;
sqlite> .exit
```

### Capturas
```bash
docker exec -it gtvision_lpr_detection ls -lh /app/captures
```

### Dados de Treinamento
```bash
docker exec -it gtvision_lpr_detection ls -lh /app/pending_training
```

## 🔍 Testar Webhook LPR

```bash
curl -X POST http://localhost:5000/lpr-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "Plate": {
      "PlateNumber": "ABC1234"
    },
    "Channel": 1,
    "DeviceName": "Camera LPR Teste"
  }'

# Verificar se salvou JSON
docker exec -it gtvision_lpr_detection ls -lh /app/received_webhooks
```

## 🐛 Troubleshooting

### Serviço não inicia
```bash
# Ver logs completos
docker-compose logs lpr_detection

# Verificar dependências
docker-compose ps
```

### Não detecta placas
```bash
# Verificar modelo YOLO
docker exec -it gtvision_lpr_detection ls -lh yolov8n.pt

# Testar detecção manual
docker exec -it gtvision_lpr_detection python -c "
from detection import PlateDetector
detector = PlateDetector('yolov8n.pt')
print('Detector carregado com sucesso!')
"
```

### Erro de conexão com backend
```bash
# Verificar variável de ambiente
docker exec -it gtvision_lpr_detection env | grep BACKEND_URL

# Testar conectividade
docker exec -it gtvision_lpr_detection curl http://backend:8000/api/health
```

## ✅ Critérios de Sucesso

- [ ] Serviço inicia sem erros
- [ ] Health check retorna OK
- [ ] Câmera RTSP processa LPR
- [ ] Câmera RTMP pula LPR
- [ ] Placas detectadas aparecem no banco
- [ ] Capturas salvas em /app/captures
- [ ] Webhook funciona
- [ ] Auto-treinamento salva dados
