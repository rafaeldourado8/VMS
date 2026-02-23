# Análise: VOD e Streaming HLS no VMS

## 📊 Status Atual

### ✅ O que JÁ EXISTE

#### 1. **Serviço VOD HLS** (`services/vod/`)
- ✅ Converte MP4 → HLS on-demand
- ✅ Cache inteligente (hash-based)
- ✅ Limpeza automática (24h)
- ✅ Endpoints REST prontos
- ✅ Docker configurado (porta 8006)
- ✅ CORS habilitado

**Endpoints disponíveis:**
```
GET  /health
GET  /vod/{video_path}/index.m3u8        # Playlist HLS
GET  /vod/{video_path}/{segment}.ts      # Segmentos
POST /cache/start/{camera_id}            # Inicia cache
POST /cache/stop/{camera_id}             # Para cache
POST /cache/cleanup                      # Limpa cache antigo
```

**Exemplo de uso:**
```
http://localhost:8006/vod/camera_1/2026-02-20/12-44-27.mp4/index.m3u8
```

#### 2. **Frontend - Player HLS Otimizado**
- ✅ `OptimizedHLSPlayer` (utils/optimizedHLSPlayer.js)
- ✅ Buffer otimizado (10s max)
- ✅ Detecção e correção de drift
- ✅ Recuperação automática de erros
- ✅ Limpeza de buffer antigo
- ✅ `MosaicPlayerManager` para múltiplos players

#### 3. **Frontend - Componentes**
- ✅ `RecordingPlayer.tsx` - Player de gravações
- ✅ `VideoPlayer.tsx` - Player genérico
- ✅ `TimelinePlayerModal.tsx` - Modal com timeline
- ✅ `WebRTCPlayer.tsx` - Player WebRTC (live)

#### 4. **Backend - Recordings API**
- ✅ Model `Recording` (camera_id, date, file_path, etc)
- ✅ ViewSet REST completo
- ✅ Filtros por câmera e data
- ✅ Sincronização com Recording Service

#### 5. **Infraestrutura**
- ✅ MediaMTX (RTSP/HLS/WebRTC)
- ✅ HAProxy (gateway unificado)
- ✅ Nginx (arquivos estáticos)
- ✅ PostgreSQL com réplicas
- ✅ Redis (cache)
- ✅ Recorder Service (gravação)
- ✅ Storage Service (indexação)

---

## ❌ O que FALTA

### 1. **Integração Backend ↔ VOD Service**
- ❌ Backend não tem endpoint para gerar URL HLS
- ❌ Falta proxy/roteamento para VOD no HAProxy/Kong
- ❌ RecordingViewSet não retorna URLs HLS

### 2. **Frontend - Uso do VOD**
- ❌ `RecordingPlayer` usa URL direta MP4 (não HLS)
- ❌ Não usa `OptimizedHLSPlayer` para gravações
- ❌ Falta integração com VOD Service

### 3. **Configuração de Roteamento**
- ❌ HAProxy não roteia `/vod/*` para VOD Service
- ❌ Kong não tem rota para VOD

---

## 🎯 Checklist de Implementação

### Fase 1: Backend Integration (10 min)
- [ ] Adicionar método `get_hls_url()` no RecordingSerializer
- [ ] Criar endpoint `GET /api/recordings/{id}/hls/` que retorna URL HLS
- [ ] Adicionar variável de ambiente `VOD_SERVICE_URL`

### Fase 2: HAProxy/Kong Routing (5 min)
- [ ] Adicionar rota `/vod/*` → `vod_hls:8004` no HAProxy
- [ ] Adicionar rota no Kong (opcional)
- [ ] Testar acesso: `http://localhost/vod/camera_1/.../index.m3u8`

### Fase 3: Frontend Integration (15 min)
- [ ] Modificar `RecordingPlayer.tsx` para usar HLS
- [ ] Integrar `OptimizedHLSPlayer` no componente
- [ ] Adicionar fallback para MP4 direto (se HLS falhar)
- [ ] Testar playback de gravações

### Fase 4: Testes (10 min)
- [ ] Testar conversão MP4 → HLS
- [ ] Testar playback no navegador
- [ ] Testar cache (verificar `/hls_cache`)
- [ ] Testar múltiplas câmeras simultâneas
- [ ] Testar seek/DVR

### Fase 5: Otimizações (Opcional)
- [ ] Implementar pré-cache de gravações recentes
- [ ] Adicionar métricas (tempo de conversão, cache hit rate)
- [ ] Implementar adaptive bitrate (múltiplas qualidades)
- [ ] Adicionar thumbnails na timeline

---

## 🔧 Arquitetura Atual vs Ideal

### Atual (Parcial)
```
Frontend → Backend API → Recordings (MP4 direto)
                       ↓
                   VOD Service (não integrado)
```

### Ideal (Completo)
```
Frontend → Backend API → VOD Service → HLS Cache → MP4 Files
              ↓              ↓
         HLS URLs      Conversão FFmpeg
```

---

## 📈 Benefícios da Implementação Completa

### Performance
- ✅ Streaming progressivo (não precisa baixar tudo)
- ✅ Seek instantâneo (pula para qualquer ponto)
- ✅ Buffer otimizado (menos memória)

### Compatibilidade
- ✅ Funciona em todos os navegadores modernos
- ✅ Suporte mobile (iOS/Android)
- ✅ Sem necessidade de plugins

### Escalabilidade
- ✅ Cache de segmentos (menos conversões)
- ✅ CDN-ready (pode usar CloudFront/CloudFlare)
- ✅ Múltiplos players simultâneos

### UX
- ✅ Playback mais suave
- ✅ Menos buffering
- ✅ Timeline interativa

---

## 🚀 Próximos Passos

1. **Implementar integração Backend ↔ VOD** (prioridade alta)
2. **Configurar roteamento HAProxy** (prioridade alta)
3. **Atualizar frontend para usar HLS** (prioridade média)
4. **Testes end-to-end** (prioridade alta)
5. **Otimizações e métricas** (prioridade baixa)

---

## 💡 Recomendação Profissional

**Status:** Sistema VOD/HLS está 70% implementado

**Ação:** Completar integração (30% restante) para ter streaming profissional

**Tempo estimado:** 40 minutos (sem otimizações)

**Impacto:** Alto - Melhora significativa na experiência de playback de gravações
