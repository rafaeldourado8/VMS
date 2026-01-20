# 🤖 AI Detection - Auto-Start Integration

Integração automática entre Backend e AI Detection Service.

## 🎯 Funcionalidade

Quando uma câmera é **criada/atualizada/deletada** no Backend, o sistema **automaticamente**:
- ✅ Inicia detecção AI se `ai_enabled=True`
- ⏸️ Para detecção AI se `ai_enabled=False`
- 🗑️ Para detecção AI se câmera é deletada

## 🔧 Como Funciona

### 1. Django Signals
**Arquivo:** `backend/apps/cameras/signals.py`

```python
@receiver(post_save, sender=Camera)
def handle_camera_save(sender, instance, created, **kwargs):
    if instance.ai_enabled:
        # POST http://ai_detection:5000/cameras/{id}/start
    else:
        # POST http://ai_detection:5000/cameras/{id}/stop

@receiver(post_delete, sender=Camera)
def handle_camera_delete(sender, instance, **kwargs):
    # POST http://ai_detection:5000/cameras/{id}/stop
```

### 2. AI Detection API
**Arquivo:** `services/ai_detection/api/control_api.py`

```python
POST /cameras/<camera_id>/start
{
  "source_url": "rtsp://..."
}

POST /cameras/<camera_id>/stop

GET /cameras  # Lista câmeras ativas
```

### 3. Fluxo Completo

```
1. Admin cria câmera com ai_enabled=True
   ↓
2. Django Signal detecta post_save
   ↓
3. Signal faz POST /cameras/{id}/start
   ↓
4. AI Detection inicia pipeline
   ↓
5. Detecções enviadas via RabbitMQ
   ↓
6. Backend recebe via WebSocket Consumer
   ↓
7. Frontend exibe em tempo real
```

## 📝 Uso

### Criar Câmera com AI

```bash
POST /api/cameras/
{
  "name": "Camera LPR 01",
  "stream_url": "rtsp://admin:pass@192.168.1.100:554/stream",
  "ai_enabled": true  # ← AI inicia automaticamente
}
```

### Habilitar AI em Câmera Existente

```bash
PATCH /api/cameras/123/
{
  "ai_enabled": true  # ← AI inicia automaticamente
}
```

### Desabilitar AI

```bash
PATCH /api/cameras/123/
{
  "ai_enabled": false  # ← AI para automaticamente
}
```

### Deletar Câmera

```bash
DELETE /api/cameras/123/  # ← AI para automaticamente
```

## 🧪 Teste

```bash
# Teste automático
python tests/test_ai_auto_start.py

# Teste manual
# 1. Criar câmera com ai_enabled=True
curl -X POST http://localhost:8000/api/cameras/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","stream_url":"rtsp://test","ai_enabled":true}'

# 2. Verificar AI Detection
curl http://localhost:5000/cameras
# Deve retornar a câmera na lista
```

## ⚙️ Configuração

### Backend (.env)
```bash
# Nenhuma configuração adicional necessária
# Signal usa URL hardcoded: http://ai_detection:5000
```

### AI Detection (.env)
```bash
API_PORT=5000  # Porta da Control API
```

### Docker Compose
```yaml
ai_detection:
  ports:
    - "5000:5000"  # Control API
  depends_on:
    - mediamtx
    - redis_cache
    - rabbitmq
```

## 🔍 Troubleshooting

### AI não inicia automaticamente

**Verificar:**
1. Signal registrado no `apps.py`:
   ```python
   def ready(self):
       import apps.cameras.signals
   ```

2. AI Detection rodando:
   ```bash
   docker-compose ps ai_detection
   curl http://localhost:5000/health
   ```

3. Logs do Backend:
   ```bash
   docker-compose logs backend | grep "AI detection"
   ```

4. Logs do AI Detection:
   ```bash
   docker-compose logs ai_detection
   ```

### Erro de conexão

**Sintoma:** `Error communicating with AI detection service`

**Solução:**
- Verificar se `ai_detection` está na mesma rede Docker
- Verificar se porta 5000 está exposta
- Testar conectividade: `docker exec backend curl http://ai_detection:5000/health`

### Câmera não aparece na lista

**Verificar:**
```bash
# Lista câmeras ativas no AI Detection
curl http://localhost:5000/cameras

# Deve retornar:
{
  "cameras": [
    {"id": 1, "url": "rtsp://..."}
  ]
}
```

## 📊 Monitoramento

### Verificar Status

```bash
# Quantas câmeras com AI ativa
curl http://localhost:5000/health
# {"status": "ok", "active_cameras": 3}

# Lista detalhada
curl http://localhost:5000/cameras
```

### Logs

```bash
# Backend (signals)
docker-compose logs -f backend | grep "AI detection"

# AI Detection (pipeline)
docker-compose logs -f ai_detection
```

## 🎯 Próximos Passos

- [ ] Adicionar retry automático se AI Detection estiver offline
- [ ] Implementar health check antes de iniciar câmera
- [ ] Dashboard mostrando status AI por câmera
- [ ] Métricas de performance (Prometheus)
