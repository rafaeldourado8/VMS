# Correção: Upload de Imagens de Detecções

## Problema
O frontend não estava exibindo os recortes das placas/veículos detectados porque:
1. O AI service enviava imagens como base64 muito grandes
2. O backend não estava preparado para receber uploads de arquivos
3. As imagens não eram salvas no sistema de arquivos

## Solução Implementada

### 1. Frame Processor (AI Service)
**Arquivo:** `services/ai_detection/frame_processor.py`

**Mudanças:**
- Alterado de JSON com base64 para **multipart/form-data**
- Envia arquivo JPEG real (compressão 85%)
- Reduz tamanho da requisição drasticamente

**Antes:**
```python
payload = {
    'image_url': f"data:image/jpeg;base64,{image_b64}"  # Muito grande!
}
response = requests.post(url, json=payload)
```

**Depois:**
```python
files = {
    'image': ('detection.jpg', buffer.tobytes(), 'image/jpeg')
}
data = {
    'camera_id': camera_id,
    'plate': plate,
    # ... outros campos
}
response = requests.post(url, data=data, files=files)
```

### 2. Backend Django
**Arquivo:** `backend/apps/deteccoes/views.py`

**Mudanças:**
- Adicionado suporte a `MultiPartParser` e `FormParser`
- Processa upload de arquivo de imagem
- Salva no diretório `media/detections/`
- Gera URL pública para a imagem

**Código adicionado:**
```python
parser_classes = [MultiPartParser, FormParser, JSONParser]

def post(self, request):
    if 'image' in request.FILES:
        image_file = request.FILES['image']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        camera_id = request.data.get('camera_id', 'unknown')
        filename = f"detections/cam_{camera_id}_{timestamp}.jpg"
        
        path = default_storage.save(filename, ContentFile(image_file.read()))
        image_url = default_storage.url(path)
```

### 3. URLs Django
**Arquivo:** `backend/config/urls.py`

**Mudanças:**
- Adicionado rota para servir arquivos de media em desenvolvimento

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 4. Estrutura de Diretórios
Criado:
```
backend/
  media/
    detections/  # Imagens das detecções
```

## Fluxo Completo

```
1. AI Service detecta veículo
   ↓
2. Recorta imagem do veículo (crop)
   ↓
3. Comprime como JPEG (85% qualidade)
   ↓
4. Envia via multipart/form-data para /api/deteccoes/ingest/
   ↓
5. Backend recebe arquivo
   ↓
6. Salva em media/detections/cam_X_TIMESTAMP.jpg
   ↓
7. Gera URL: /media/detections/cam_X_TIMESTAMP.jpg
   ↓
8. Salva URL no banco de dados
   ↓
9. Frontend busca detecções via /api/detections/
   ↓
10. Exibe imagem usando image_url do banco
```

## Formato da Imagem Salva

**Nome do arquivo:**
```
cam_{camera_id}_{timestamp}.jpg
```

**Exemplo:**
```
cam_1_20260105_143022.jpg
cam_3_20260105_143045.jpg
```

## Configurações Django

**settings.py:**
```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

**Já estava configurado!** ✅

## Testando

### 1. Verificar se imagens estão sendo salvas:
```bash
ls -la backend/media/detections/
```

### 2. Verificar no banco de dados:
```sql
SELECT id, camera_id, plate, image_url 
FROM deteccoes_deteccao 
ORDER BY timestamp DESC 
LIMIT 5;
```

### 3. Acessar imagem diretamente:
```
http://localhost:8000/media/detections/cam_1_20260105_143022.jpg
```

### 4. Verificar no frontend:
- Ir para página "Detecções"
- Clicar em uma detecção
- Deve exibir a imagem do veículo

## Vantagens da Solução

1. **Performance:** Arquivos JPEG são muito menores que base64
2. **Escalabilidade:** Fácil migrar para S3/CloudFront depois
3. **Padrão:** Usa sistema de arquivos do Django (default_storage)
4. **Compatibilidade:** Funciona com qualquer storage backend

## Próximos Passos (Produção)

Para produção, considere:

1. **Usar S3 ou similar:**
```python
# settings.py
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'gtvision-detections'
```

2. **CDN (CloudFront):**
- Servir imagens via CDN
- Reduzir latência
- Cache automático

3. **Limpeza automática:**
- Celery task para deletar imagens antigas
- Respeitar retention policy (30 dias padrão)

4. **Compressão adicional:**
- WebP para navegadores modernos
- Thumbnails para listagem

## Arquivos Modificados

1. `services/ai_detection/frame_processor.py`
2. `backend/apps/deteccoes/views.py`
3. `backend/config/urls.py`

## Conclusão

✅ Imagens agora são salvas corretamente
✅ Frontend pode exibir recortes das detecções
✅ Sistema pronto para escalar para cloud storage
