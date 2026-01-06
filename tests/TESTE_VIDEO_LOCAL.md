# Teste de Detecção com Vídeo Local

## Objetivo
Testar o sistema de detecção usando um vídeo de carros ao invés de stream RTSP.

## Pré-requisitos

### 1. Instalar dependências Python (no host Windows)
```bash
pip install opencv-python requests numpy
```

### 2. Vídeo de teste
Coloque o vídeo `video_carros.mp4` na raiz do projeto VMS:
```
d:\VMS\video_carros.mp4
```

### 3. Backend rodando
Certifique-se de que o backend está rodando:
```bash
docker-compose up -d backend
```

## Como Executar

### Opção 1: Teste Simples (Recomendado)
Roda no host Windows, sem precisar de YOLO:

```bash
cd d:\VMS
python test_video_simple.py
```

**O que faz:**
- Lê o vídeo `video_carros.mp4`
- Processa 1 frame a cada 2 segundos
- Recorta região central do frame
- Envia como detecção para o backend
- Limita a 5 detecções para teste

### Opção 2: Teste Completo (com YOLO)
Roda dentro do container AI Detection:

```bash
# 1. Copiar vídeo para o container
docker cp video_carros.mp4 gtvision_ai_detection:/app/video_carros.mp4

# 2. Executar teste
docker exec -it gtvision_ai_detection python test_video_detection.py
```

## Verificar Resultados

### 1. Logs do teste
Você verá no console:
```
🚀 Iniciando teste com vídeo: video_carros.mp4
📹 Vídeo: 1200 frames @ 30.00 FPS
🔍 Frame 60/1200
✅ Detecção 1 enviada
🔍 Frame 120/1200
✅ Detecção 2 enviada
...
🏁 Teste concluído: 5 detecções enviadas
```

### 2. Verificar no banco de dados
```sql
SELECT id, camera_id, plate, vehicle_type, confidence, image_url, timestamp 
FROM deteccoes_deteccao 
ORDER BY timestamp DESC 
LIMIT 10;
```

### 3. Verificar imagens salvas
```bash
ls -la backend/media/detections/
```

Deve mostrar arquivos como:
```
cam_1_20260105_154530.jpg
cam_1_20260105_154532.jpg
...
```

### 4. Verificar no frontend
1. Abra http://localhost
2. Faça login
3. Vá em "Detecções"
4. Deve ver as detecções com imagens

### 5. Acessar imagem diretamente
```
http://localhost:8000/media/detections/cam_1_20260105_154530.jpg
```

## Troubleshooting

### Erro: "Não foi possível abrir vídeo"
- Verifique se o arquivo existe: `dir video_carros.mp4`
- Verifique o nome do arquivo (case-sensitive)
- Tente caminho absoluto: `d:\VMS\video_carros.mp4`

### Erro: "Connection refused"
- Verifique se o backend está rodando: `docker ps | grep backend`
- Teste o endpoint: `curl http://localhost:8000/admin/login/`

### Erro: "401 Unauthorized" ou "403 Forbidden"
- Verifique a API Key no arquivo `.env`:
  ```
  INGEST_API_KEY=your-ingest-api-key-here
  ```
- Atualize a API Key no script de teste

### Erro: "500 Internal Server Error"
- Verifique logs do backend: `docker logs gtvision_backend`
- Verifique se a câmera ID existe no banco

## Próximos Passos

Se o teste funcionar:
1. ✅ Sistema de ingestão está OK
2. ✅ Upload de imagens está OK
3. ✅ Backend está salvando corretamente

Se não funcionar:
1. Verifique logs do backend
2. Verifique permissões da pasta `media/`
3. Verifique se a câmera existe no banco

## Integração com Stream Real

Depois que o teste funcionar, você pode:

1. **Modificar stream_worker.py** para usar vídeo local:
```python
# Ao invés de HLS
stream_url = f"http://mediamtx:8889/cam_{camera_id}/index.m3u8"

# Use vídeo local
stream_url = "/app/video_carros.mp4"
```

2. **Ou configurar câmera com vídeo local:**
```python
# No frontend, ao criar câmera:
stream_url = "file:///app/video_carros.mp4"
```

## Comandos Úteis

```bash
# Ver logs do backend
docker logs -f gtvision_backend

# Ver logs do AI service
docker logs -f gtvision_ai_detection

# Limpar detecções antigas
docker exec -it gtvision_postgres psql -U gtvision_user -d gtvision_db -c "DELETE FROM deteccoes_deteccao;"

# Reiniciar serviços
docker-compose restart backend ai_detection
```
