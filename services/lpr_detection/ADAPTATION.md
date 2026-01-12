# ✅ Adaptação do LEGACY - LPR Detection

## 📦 O que foi mantido (100% funcional)

### Código LEGACY copiado:
- ✅ `detection.py` - YOLO + Fast-Plate-OCR
- ✅ `yolov8n.pt` - Modelo treinado
- ✅ `fast-plate-ocr-master/` - Biblioteca OCR
- ✅ `database/` - SQLite local
- ✅ `alert_system/` - Logs e alarmes
- ✅ `api_client.py` - Comunicação com backend
- ✅ `prepare_dataset.py` - Auto-treinamento
- ✅ `requirements.txt` - Dependências

## 🔧 Adaptações Mínimas

### 1. URL do Backend
```python
# Antes
API_BASE_URL = "http://gt-vision-backend:8000"

# Depois
API_BASE_URL = os.getenv("BACKEND_URL", "http://backend:8000")
```

### 2. Lógica RTSP/RTMP
```python
def should_enable_lpr(camera_url: str) -> bool:
    """RTSP = LPR ativo | RTMP = apenas gravação"""
    if not camera_url:
        return False
    return camera_url.lower().startswith('rtsp://')
```

### 3. Verificação no Processamento
```python
def process_camera_stream(...):
    # Verifica se deve processar LPR
    if not should_enable_lpr(rtsp_url):
        logging.info(f"Câmera {camera_name} é RTMP (bullet), pulando LPR")
        return
    
    # Continua processamento normal...
```

## 🚀 Como Usar

### Build
```bash
cd services/lpr_detection
docker build -t gtvision/lpr_detection:latest .
```

### Run
```bash
docker run -d \
  --name lpr_detection \
  -e BACKEND_URL=http://backend:8000 \
  -e ADMIN_API_KEY=your_key \
  -v $(pwd)/captures:/app/captures \
  gtvision/lpr_detection:latest
```

### Integração no docker-compose.yml
```yaml
lpr_detection:
  build: ./services/lpr_detection
  container_name: gtvision_lpr_detection
  environment:
    BACKEND_URL: http://backend:8000
    ADMIN_API_KEY: ${ADMIN_API_KEY}
  volumes:
    - lpr_captures:/app/captures
    - lpr_training:/app/pending_training
  networks:
    - gtvision_network
  restart: unless-stopped
```

## 📊 Funcionamento

### Câmeras RTSP (LPR)
1. Recebe stream RTSP
2. YOLO detecta placas
3. Fast-Plate-OCR reconhece texto
4. Salva no banco local
5. Envia para backend
6. Salva para auto-treinamento

### Câmeras RTMP (Bullets)
1. Detecta protocolo RTMP
2. **Pula processamento LPR**
3. Apenas grava (MediaMTX)

## 🎯 Próximos Passos

1. [ ] Adicionar ao docker-compose.yml
2. [ ] Testar com câmera RTSP real
3. [ ] Testar com câmera RTMP (deve pular)
4. [ ] Integrar com Recording Service (futuro)
5. [ ] Processar gravações ao invés de tempo real (futuro)

## 💡 Vantagens de Usar o LEGACY

- ✅ Modelo já treinado e funcional
- ✅ Fast-Plate-OCR testado e aprovado
- ✅ Auto-treinamento implementado
- ✅ Webhook LPR suportado
- ✅ Banco local para cache
- ✅ Zero mudanças no core (apenas adaptações mínimas)
