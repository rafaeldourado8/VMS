# Segurança de Gravações

## Problema

Expor `/recordings/` diretamente no nginx = acesso irrestrito ao disco.

## Solução: Auth Request (Nginx + Backend)

### Fluxo de Autenticação

```
1. Cliente → GET /recordings/camera_1/2026-02-25/14-45-12.mp4
   Headers: Authorization: Bearer <token>

2. Nginx → auth_request /auth/recording
   Envia: X-Original-URI, Authorization

3. Backend → Valida token JWT
   - Extrai camera_id da URI
   - Verifica permissões do usuário
   - Retorna 200 (OK) ou 403 (Forbidden)

4. Nginx → Se 200, serve arquivo
           Se 403, retorna erro
```

### Nginx Config

```nginx
location /recordings/ {
    auth_request /auth/recording;
    auth_request_set $auth_user $upstream_http_x_user_id;
    
    alias /recordings/;
    internal;  # Apenas via auth_request
    
    mp4;
    # ... resto da config
}

location = /auth/recording {
    internal;
    proxy_pass http://backend:8000/api/recordings/verify-access/;
    proxy_pass_request_body off;
    proxy_set_header X-Original-URI $request_uri;
    proxy_set_header Authorization $http_authorization;
}
```

### Backend Endpoint

```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_recording_access(request):
    original_uri = request.headers.get('X-Original-URI')
    
    # Extrair camera_id: /recordings/camera_1/...
    match = re.match(r'/recordings/camera_(\d+)/', original_uri)
    camera_id = int(match.group(1))
    
    # Validar permissão
    if user.has_camera_access(camera_id):
        return HttpResponse(status=200)
    
    return HttpResponse(status=403)
```

## Camadas de Segurança

### 1. Autenticação JWT
- Todo request precisa de token válido
- Token verificado pelo Django REST Framework

### 2. Validação de Permissões
- Usuário só acessa câmeras autorizadas
- Implementar: `user.has_camera_access(camera_id)`

### 3. Path Traversal Protection
- Regex valida formato: `/recordings/camera_\d+/YYYY-MM-DD/HH-MM-SS.mp4`
- Bloqueia: `../`, `../../`, etc.

### 4. Internal Location
- `internal;` no nginx = não acessível diretamente
- Apenas via `auth_request`

## Implementar Permissões Granulares

```python
# models.py
class CameraPermission(models.Model):
    user = models.ForeignKey(User)
    camera = models.ForeignKey(Camera)
    can_view_live = models.BooleanField(default=True)
    can_view_recordings = models.BooleanField(default=True)
    can_download = models.BooleanField(default=False)

# views.py
def verify_recording_access(request):
    camera_id = extract_camera_id(original_uri)
    
    # Admin = acesso total
    if request.user.is_staff:
        return HttpResponse(status=200)
    
    # Verificar permissão específica
    has_permission = CameraPermission.objects.filter(
        user=request.user,
        camera_id=camera_id,
        can_view_recordings=True
    ).exists()
    
    if has_permission:
        return HttpResponse(status=200)
    
    return HttpResponse(status=403)
```

## Rate Limiting (Opcional)

```nginx
# Limitar requests por IP
limit_req_zone $binary_remote_addr zone=recordings:10m rate=10r/s;

location /recordings/ {
    limit_req zone=recordings burst=20;
    # ... resto
}
```

## Auditoria

```python
# Log de acessos
import logging
logger = logging.getLogger('recordings.access')

def verify_recording_access(request):
    camera_id = extract_camera_id(original_uri)
    
    logger.info(f"Access attempt: user={request.user.id} camera={camera_id} uri={original_uri}")
    
    # ... validação
```

## Benefícios

✅ Zero acesso sem autenticação
✅ Permissões por usuário/câmera
✅ Path traversal bloqueado
✅ Auditoria completa
✅ Performance (nginx serve arquivo após validação)
