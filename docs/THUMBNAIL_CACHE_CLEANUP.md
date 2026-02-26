# Limpeza de Cache de Thumbnails

## Problema
As thumbnails de câmeras ficavam em cache mesmo após a câmera ser deletada, mostrando imagens antigas de câmeras que não existem mais.

## Solução Implementada

### 1. Backend (Django)
- **Método `clear_cache()`** em `ThumbnailService` para limpar cache específico
- **Integração automática** no endpoint DELETE de câmeras
- **Endpoints manuais** para limpeza sob demanda:
  - `POST /api/thumbnails/clear/` - Limpa todo o cache
  - `POST /api/thumbnails/{camera_id}/clear/` - Limpa cache de uma câmera

### 2. Frontend (React)
- **Limpeza automática** no `cameraStore` quando câmeras são removidas
- **Componente `ClearCacheButton`** para limpeza manual
- **Atualização do `StreamThumbnail`** para reagir a mudanças de status

## Como Usar

### Limpeza Automática
Quando você deleta uma câmera, o cache é limpo automaticamente:
```typescript
// No cameraStore
removeCamera(id) // Limpa cache automaticamente
```

### Limpeza Manual (Frontend)
```tsx
import { ClearCacheButton } from '@/components/cameras/ClearCacheButton'

// Adicione o botão onde precisar
<ClearCacheButton />
```

### Limpeza Manual (API)
```bash
# Limpar cache de uma câmera específica
curl -X POST http://localhost/api/thumbnails/1/clear/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Limpar todo o cache
curl -X POST http://localhost/api/thumbnails/clear/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Arquivos Modificados

### Backend
- `backend/apps/thumbnails/services.py` - Adicionado método `clear_cache()`
- `backend/apps/thumbnails/views.py` - Adicionado endpoint `clear_thumbnail_cache()`
- `backend/apps/thumbnails/urls.py` - Adicionadas rotas de limpeza
- `backend/apps/cameras/views.py` - Integrada limpeza no DELETE

### Frontend
- `frontend/src/components/cameras/StreamThumbnail.tsx` - Atualizado para reagir a mudanças
- `frontend/src/components/cameras/ClearCacheButton.tsx` - Novo componente
- `frontend/src/store/cameraStore.ts` - Já tinha lógica de limpeza

## Cache em Dois Níveis

1. **Backend (Django Cache)**: 30 segundos
   - Limpo automaticamente ao deletar câmera
   - Limpo via endpoint `/api/thumbnails/clear/`

2. **Frontend (IndexedDB)**: 24 horas
   - Limpo automaticamente pelo `cameraStore`
   - Limpo via `ClearCacheButton`

## Teste
Execute o script de teste:
```bash
tests\test_cache_clear.bat
```
