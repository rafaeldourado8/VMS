# Integração VOD/HLS Completa ✅

## Mudanças Implementadas

### 1. ✅ HAProxy - Roteamento VOD
**Arquivo**: `haproxy/haproxy.cfg`

```cfg
# Linha 66 - ACL para VOD
acl is_vod_hls path_beg /vod/

# Linha 72 - Roteamento
use_backend vod_hls_service if is_vod_hls

# Backend configurado
backend vod_hls_service
    mode http
    server vod_hls1 vod_hls:8004 check
```

**Status**: ✅ Já estava configurado

---

### 2. ✅ Frontend - Variável de Ambiente
**Arquivo**: `frontend/.env`

```env
# Storage Service URL (via HAProxy)
VITE_STORAGE_URL=http://localhost/storage
```

**Uso**: Todas as chamadas ao Storage Service agora usam HAProxy

---

### 3. ✅ Frontend - TimelinePlayerModal
**Arquivo**: `frontend/src/components/cameras/TimelinePlayerModal.tsx`

**Antes**:
```tsx
const { data } = await axios.get(`http://localhost:8003/recordings/available-dates/${camera.id}`)
```

**Depois**:
```tsx
const storageUrl = import.meta.env.VITE_STORAGE_URL || '/storage'
const { data } = await axios.get(`${storageUrl}/recordings/available-dates/${camera.id}`)
```

**URL HLS**: Já usa rota relativa via HAProxy
```tsx
const masterPlaylistUrl = `/vod/playlist/${camera.id}/${selectedDate}/index.m3u8`
```

---

### 4. ✅ Frontend - API Service
**Arquivo**: `frontend/src/services/api.ts`

**recordingService**:
```typescript
async list(params: { camera_id: number; date: string }) {
  const storageUrl = import.meta.env.VITE_STORAGE_URL || '/storage'
  const { data } = await axios.get(`${storageUrl}/timeline/${params.camera_id}`, {
    params: { date: params.date, limit: 100 }
  })
  // ...
}
```

**timelineService**:
```typescript
async getTimeline(cameraId: number, date?: string) {
  const storageUrl = import.meta.env.VITE_STORAGE_URL || '/storage'
  const { data } = await axios.get(`${storageUrl}/timeline/${cameraId}`, { params })
  return data
}
```

---

## Fluxo Completo

```
Frontend (React)
    ↓
HAProxy (porta 80)
    ↓
┌─────────────────┬─────────────────┐
│                 │                 │
Storage Service   VOD HLS Service
(porta 8003)      (porta 8004)
    ↓                 ↓
PostgreSQL        FFmpeg (on-demand)
    ↓                 ↓
/recordings/      HLS Segments (.ts)
```

### URLs Finais

| Serviço | URL Antiga (❌) | URL Nova (✅) |
|---------|----------------|--------------|
| Storage Timeline | `http://localhost:8003/timeline/...` | `/storage/timeline/...` |
| Storage Dates | `http://localhost:8003/recordings/available-dates/...` | `/storage/recordings/available-dates/...` |
| VOD Playlist | `http://localhost:8004/vod/playlist/...` | `/vod/playlist/...` |
| VOD Segments | `http://localhost:8004/vod/segment/...` | `/vod/segment/...` |

---

## Backend Recordings App

**Status**: ❌ NÃO USADO

O app `backend/apps/recordings/` não é utilizado. Todo o sistema de gravações funciona via:
- **Recorder Service**: Grava vídeos
- **Storage Service**: Indexa e serve gravações
- **VOD Service**: Converte MP4 → HLS on-demand

**Recomendação**: Pode ser removido ou mantido para futuras integrações.

---

## Testes

### 1. Testar Storage via HAProxy
```bash
curl http://localhost/storage/recordings/available-dates/1
```

### 2. Testar VOD via HAProxy
```bash
curl http://localhost/vod/playlist/1/2026-02-25/index.m3u8
```

### 3. Testar Frontend
1. Abrir Timeline de uma câmera
2. Verificar Network tab: todas as requests devem ir para `localhost` (não `localhost:8003` ou `localhost:8004`)
3. Playback deve funcionar normalmente

---

## Benefícios

✅ **Gateway Unificado**: Todas as requests passam pelo HAProxy (porta 80)
✅ **Sem CORS**: Tudo no mesmo domínio
✅ **Produção Ready**: Fácil trocar backend sem mudar frontend
✅ **Load Balancing**: HAProxy pode distribuir carga entre múltiplas instâncias
✅ **Monitoramento**: HAProxy Stats em `http://localhost:8404/stats`

---

## Próximos Passos (Opcional)

1. **Cache Redis no VOD**: Cachear playlists por 60s
2. **Métricas**: Adicionar Prometheus/Grafana
3. **CDN**: Configurar CloudFront para servir HLS
4. **Adaptive Bitrate**: Múltiplas qualidades (360p, 720p, 1080p)
