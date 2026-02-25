# Correção de Rotas - Clips

## Problema Original

Ao tentar criar clips, os seguintes erros ocorriam:

```
401 (Unauthorized) - api/cameras/
404 (Not Found) - api/clips/1/video/
404 (Not Found) - video/
```

## Causa Raiz

1. **Rota duplicada**: O DefaultRouter do Django estava criando `/api/clips/clips/` em vez de `/api/clips/`
2. **401 em cameras**: Token de autenticação pode ter expirado ou não estar sendo enviado
3. **404 em video**: Rota não estava sendo registrada corretamente

## Solução Implementada

### 1. Correção das Rotas (backend/apps/clips/urls.py)

**Antes:**
```python
router = DefaultRouter()
router.register(r'clips', ClipViewSet, basename='clips')
router.register(r'mosaicos', MosaicoViewSet, basename='mosaicos')

urlpatterns = [
    path('', include(router.urls)),
]
```

**Depois:**
```python
clip_list = ClipViewSet.as_view({'get': 'list', 'post': 'create'})
clip_detail = ClipViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})
clip_video = ClipViewSet.as_view({'get': 'video'})

urlpatterns = [
    path('clips/', clip_list, name='clip-list'),
    path('clips/<int:pk>/', clip_detail, name='clip-detail'),
    path('clips/<int:pk>/video/', clip_video, name='clip-video'),
    path('mosaicos/', mosaico_list, name='mosaico-list'),
    path('mosaicos/<int:pk>/', mosaico_detail, name='mosaico-detail'),
]
```

### 2. Rotas Finais

Com a configuração em `config/urls.py`:
```python
path("api/", include("apps.clips.urls")),
```

As rotas ficam:
- `POST /api/clips/` - Criar clip
- `GET /api/clips/` - Listar clips
- `GET /api/clips/{id}/` - Detalhes do clip
- `GET /api/clips/{id}/video/` - Download do vídeo
- `DELETE /api/clips/{id}/` - Remover clip

## Teste

Para testar se as rotas estão funcionando:

```bash
# Reiniciar o backend
docker-compose restart backend

# Ou se estiver rodando localmente
cd backend
python manage.py runserver
```

## Próximos Passos

Se o erro 401 persistir em `/api/cameras/`:
1. Verificar se o usuário está autenticado
2. Verificar se o token não expirou
3. Verificar o localStorage: `gtvision-auth`
4. Fazer logout e login novamente
