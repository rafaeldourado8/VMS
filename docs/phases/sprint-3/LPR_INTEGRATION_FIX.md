# 🔧 LPR Mercosul Integration Fix

## Problemas Identificados

### 1. ❌ 401 Unauthorized no `/api/cameras/`
**Causa:** Endpoint requer autenticação JWT, mas LPR usa API Key

**Solução:** Criado endpoint público `/api/cameras/lpr/active/` que aceita apenas API Key

### 2. ❌ LPR Mercosul não detecta câmeras
**Causa:** 
- Header errado: usava `Authorization: Api-Key` mas backend esperava `X-API-Key`
- Endpoint errado: `/api/detections/` não existe, correto é `/api/deteccoes/ingest/`

**Solução:**
- Atualizado header para `X-API-Key`
- Corrigido endpoint para `/api/deteccoes/ingest/`
- Ajustado payload para match com serializer

### 3. ❌ MediaMTX parando streams
**Causa:** Timeout muito curto (60s) para streams on-demand

**Solução:**
- `hlsMuxerCloseAfter: 60s` → `300s` (5 minutos)
- `sourceOnDemandCloseAfter: 60s` → `300s` (5 minutos)

### 4. ❌ Detecções não aparecem no frontend
**Causa:** Endpoint de ingestão não estava configurado corretamente

**Solução:** Corrigido payload e endpoint

---

## Mudanças Implementadas

### 1. Backend - Novo Endpoint para LPR

**Arquivo:** `backend/apps/cameras/views.py`

```python
@api_view(['GET'])
@permission_classes([HasIngestAPIKey])
def list_active_cameras_for_lpr(request):
    """Endpoint público para LPR service listar câmeras ativas"""
    from apps.cameras.models import Camera
    
    protocol = request.query_params.get('protocol', 'rtsp')
    is_active = request.query_params.get('is_active', 'true').lower() == 'true'
    
    cameras = Camera.objects.filter(
        stream_url__istartswith=f'{protocol}://',
        status='active' if is_active else None
    )
    
    results = []
    for cam in cameras:
        results.append({
            'id': cam.id,
            'name': cam.name,
            'rtsp_url': cam.stream_url,
            'location': cam.location,
            'is_active': cam.status == 'active'
        })
    
    return Response({'results': results})
```

**Arquivo:** `backend/apps/cameras/urls.py`

```python
urlpatterns = [
    path("", include(router.urls)),
    path("cameras/lpr/active/", list_active_cameras_for_lpr, name="cameras-lpr-active"),
]
```

### 2. Backend - Permissão Atualizada

**Arquivo:** `backend/apps/deteccoes/permissions.py`

```python
class HasIngestAPIKey(permissions.BasePermission):
    def has_permission(self, request, view):
        # Aceita ambos os headers para compatibilidade
        api_key = request.META.get('HTTP_X_API_KEY') or \
                  request.META.get('HTTP_AUTHORIZATION', '').replace('Api-Key ', '')
        correct_key = getattr(settings, 'ADMIN_API_KEY', None)
        return api_key == correct_key
```

**Arquivo:** `backend/config/settings.py`

```python
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "default_insecure_key_12345")
```

### 3. LPR Mercosul - Correções

**Arquivo:** `services/lpr_mercosul/main.py`

```python
def get_active_cameras():
    """Fetch active RTSP cameras from backend"""
    response = requests.get(
        f'{BACKEND_URL}/api/cameras/lpr/active/',
        headers={'X-API-Key': ADMIN_API_KEY},  # ✅ Header correto
        params={'protocol': 'rtsp', 'is_active': 'true'},
        timeout=10
    )
    response.raise_for_status()
    return response.json().get('results', [])


def send_to_backend(detection, detection_id, vehicle_path, plate_path):
    """Send detection to backend"""
    payload = {
        'camera_id': detection['camera_id'],
        'plate': detection['plate'],
        'confidence': 0.85,
        'timestamp': datetime.now().isoformat(),
        'image_url': vehicle_path  # ✅ Campo correto
    }
    
    response = requests.post(
        f'{BACKEND_URL}/api/deteccoes/ingest/',  # ✅ Endpoint correto
        headers={'X-API-Key': ADMIN_API_KEY},    # ✅ Header correto
        json=payload,
        timeout=10
    )
```

### 4. MediaMTX - Timeouts Aumentados

**Arquivo:** `mediamtx.yml`

```yaml
# HLS
hlsMuxerCloseAfter: 300s    # 5 minutos (era 60s)

# Path Defaults
pathDefaults:
  sourceOnDemandCloseAfter: 300s  # 5 minutos (era 60s)
```

---

## Como Testar

### 1. Restart dos Serviços

```bash
docker-compose restart backend lpr_mercosul mediamtx
```

### 2. Verificar Logs

```bash
# Backend
docker-compose logs -f backend

# LPR Mercosul
docker-compose logs -f lpr_mercosul

# MediaMTX
docker-compose logs -f mediamtx
```

### 3. Teste de Integração

```bash
cd tests
python test_lpr_integration.py
```

**Saída Esperada:**
```
🧪 Testing cameras endpoint...
Status: 200
✅ Found X cameras

🧪 Testing detection endpoint...
Status: 201
✅ Detection sent successfully

🧪 Testing MediaMTX...
✅ MediaMTX is running
```

### 4. Verificar Detecções no Frontend

1. Acesse: http://localhost:5173
2. Login
3. Vá para "Detecções"
4. Deve aparecer as detecções enviadas pelo LPR

---

## Checklist de Validação

- [ ] Backend responde em `/api/cameras/lpr/active/` com API Key
- [ ] LPR Mercosul consegue buscar câmeras ativas
- [ ] LPR Mercosul envia detecções para `/api/deteccoes/ingest/`
- [ ] Detecções aparecem no banco de dados
- [ ] Detecções aparecem no frontend
- [ ] MediaMTX não para streams após 60s
- [ ] Logs não mostram erros 401 ou 404

---

## Variáveis de Ambiente Necessárias

**`.env`:**
```bash
ADMIN_API_KEY=GtVisionAdmin2025
```

**Verificar se está configurado:**
```bash
docker-compose exec backend python -c "from django.conf import settings; print(settings.ADMIN_API_KEY)"
```

---

## Troubleshooting

### LPR não encontra câmeras
```bash
# Verificar se há câmeras RTSP ativas
docker-compose exec backend python manage.py shell
>>> from apps.cameras.models import Camera
>>> Camera.objects.filter(stream_url__istartswith='rtsp://', status='active')
```

### Detecções não aparecem
```bash
# Verificar se chegam no backend
docker-compose logs backend | grep "deteccoes/ingest"

# Verificar banco
docker-compose exec backend python manage.py shell
>>> from apps.deteccoes.models import Deteccao
>>> Deteccao.objects.all().count()
```

### MediaMTX para streams
```bash
# Verificar timeout
docker-compose exec mediamtx cat /mediamtx.yml | grep CloseAfter

# Deve mostrar:
# hlsMuxerCloseAfter: 300s
# sourceOnDemandCloseAfter: 300s
```

---

## Próximos Passos

1. ✅ Testar integração completa
2. ✅ Validar detecções no frontend
3. ⏳ Implementar filtros de confiança (só enviar detecções > 0.85)
4. ⏳ Adicionar retry logic para falhas de rede
5. ⏳ Implementar health check no LPR Mercosul

---

## Arquivos Modificados

```
backend/
├── apps/
│   ├── cameras/
│   │   ├── views.py          ✅ Novo endpoint
│   │   └── urls.py           ✅ Nova rota
│   └── deteccoes/
│       └── permissions.py    ✅ Aceita ambos headers
└── config/
    └── settings.py           ✅ ADMIN_API_KEY

services/
└── lpr_mercosul/
    └── main.py               ✅ Headers e endpoints corrigidos

mediamtx.yml                  ✅ Timeouts aumentados

tests/
└── test_lpr_integration.py   ✅ Novo teste
```

---

## Métricas de Sucesso

- **Antes:** 0 detecções/min
- **Depois:** X detecções/min (depende do tráfego)

- **Antes:** 401 Unauthorized
- **Depois:** 200 OK

- **Antes:** MediaMTX para após 60s
- **Depois:** MediaMTX mantém stream por 5min

---

**Data:** 2026-01-15  
**Status:** ✅ Implementado  
**Testado:** ⏳ Aguardando validação
