# 🚀 Otimização de Requests na Timeline

## 📋 Problema Identificado

Ao abrir o **TimelinePlayerModal**, múltiplos requests HTTP aparecem no DevTools:

1. **Request inicial**: `/storage/timeline/{camera_id}` retorna metadados dos blocos
2. **Requests de vídeo**: Para cada segmento MP4 (ex: `/recordings/camera_3/2026-03-03/00-56-58.mp4`)

### Por que isso acontece?

- Cada segmento de gravação é um arquivo MP4 separado (60 segundos)
- O navegador precisa fazer um request HTTP para cada arquivo
- Isso é **normal e esperado** para streaming de vídeo segmentado

## ✅ Solução Implementada

### 1. Cache Agressivo no Nginx

**Arquivo**: `nginx/nginx.conf`

```nginx
location /recordings/ {
    # Cache de 1 hora com immutable
    add_header Cache-Control "public, max-age=3600, immutable";
    
    # Buffers maiores para MP4
    mp4_buffer_size 4m;
    mp4_max_buffer_size 20m;
    
    # Otimizações de rede
    tcp_nodelay on;
    
    # Desabilitar logs para reduzir overhead
    access_log off;
}
```

**Benefícios**:
- Segmentos já carregados não são baixados novamente
- `immutable` indica ao navegador que o arquivo nunca muda
- Reduz drasticamente requests repetidos

### 2. Blob URL (Reduz Requests Visíveis)

**Arquivo**: `frontend/src/components/cameras/TimelinePlayerModal.tsx`

```typescript
// Baixar vídeo via fetch e criar Blob URL
const response = await fetch(currentVideoUrl, {
  cache: 'force-cache'
})
const blob = await response.blob()
const blobUrl = URL.createObjectURL(blob)
video.src = blobUrl
```

**Benefícios**:
- Apenas 1 request por segmento (fetch inicial)
- Seek no vídeo não gera novos requests 206
- DevTools mostra muito menos requests
- Cache do navegador ainda funciona

**Trade-offs**:
- Usa mais memória (Blob na RAM)
- Download completo antes de reproduzir

### 3. Otimizações de Rede

**HAProxy** (`haproxy/haproxy.cfg`):
```haproxy
backend nginx_recordings
    timeout server 300s
    http-response set-header Access-Control-Allow-Headers "Range, Authorization"
```

**Benefícios**:
- Suporte completo para Range requests (seek no vídeo)
- Timeout maior para downloads grandes
- CORS configurado corretamente

## 📊 Resultados Esperados

### Antes (URL Direta)
- ❌ 100+ requests visíveis no DevTools
- ❌ Múltiplos requests 206 (Range) por segmento
- ❌ Re-download de segmentos já vistos
- ❌ Latência entre segmentos

### Depois (Blob URL + Cache)
- ✅ 1 request por segmento (fetch inicial)
- ✅ Seek no vídeo não gera novos requests
- ✅ Requests em cache (304 Not Modified)
- ✅ Transições suaves entre segmentos
- ✅ 70-90% menos requests visíveis no DevTools

## 🔍 Como Validar

### 1. Verificar Cache no DevTools

1. Abrir DevTools → Network
2. Reproduzir timeline
3. Voltar para segmento já visto
4. Verificar: `Status: 200 (from disk cache)` ou `304 Not Modified`

### 2. Verificar Prefetch

1. DevTools → Network
2. Filtrar por `prefetch`
3. Ver próximo segmento sendo carregado em background

### 3. Medir Latência

```bash
# Testar cache
curl -I http://localhost/recordings/camera_3/2026-03-03/00-56-58.mp4

# Verificar headers
Cache-Control: public, max-age=3600, immutable
Accept-Ranges: bytes
```

## 🎯 Limitações

### Por que os requests ainda aparecem?

**Isso é PARCIALMENTE inevitável**:
- Arquitetura de streaming segmentado (HLS-like)
- Cada segmento é um arquivo independente
- Navegador faz Range requests (206) para seek

### Solução Implementada: Blob URL

**Antes** (URL direta):
```typescript
video.src = '/recordings/camera_3/2026-03-03/00-56-58.mp4'
// Resultado: Múltiplos requests 206 visíveis no DevTools
```

**Depois** (Blob URL):
```typescript
const response = await fetch(videoUrl, { cache: 'force-cache' })
const blob = await response.blob()
const blobUrl = URL.createObjectURL(blob)
video.src = blobUrl // blob:http://localhost/abc-123
// Resultado: 1 request inicial, depois Blob local (sem requests visíveis)
```

**Benefícios**:
- ✅ Apenas 1 request por segmento (fetch inicial)
- ✅ Seek no vídeo não gera novos requests
- ✅ DevTools mostra menos requests
- ✅ Cache do navegador ainda funciona

**Limitações**:
- ⚠️ Usa mais memória (Blob armazenado na RAM)
- ⚠️ Download completo antes de reproduzir (sem streaming progressivo)

### Alternativas (não recomendadas)

1. **Concatenar todos os MP4 em um único arquivo**
   - ❌ Problema: Arquivo gigante (horas de vídeo)
   - ❌ Problema: Seek lento
   - ❌ Problema: Impossível fazer range requests eficientes

2. **Usar HLS nativo (.m3u8)**
   - ❌ Problema: Precisa transcodificar gravações
   - ❌ Problema: Overhead de processamento
   - ❌ Problema: Latência adicional

3. **Usar WebRTC para playback**
   - ❌ Problema: Não funciona para gravações antigas
   - ❌ Problema: Complexidade adicional

## 🛡️ Segurança

### Autenticação (TODO - FASE 2)

Atualmente `/recordings/` é público. Para produção:

```nginx
location /recordings/ {
    # Validar token JWT
    auth_request /auth/validate;
    auth_request_set $auth_status $upstream_status;
}
```

### Rate Limiting

Já implementado no HAProxy:
```haproxy
# 200 requests/10s por IP
http-request deny deny_status 429 if { sc_http_req_rate(0) gt 200 }
```

## 📈 Monitoramento

### Métricas Importantes

1. **Cache Hit Rate**: % de requests servidos do cache
2. **Latência de Transição**: Tempo entre segmentos
3. **Bandwidth**: Uso de banda por usuário

### Logs

```bash
# Ver requests de recordings (se access_log estiver habilitado)
docker logs nginx 2>&1 | grep "/recordings/"

# Ver cache hits no HAProxy
curl http://localhost:8404/stats
```

## 🔧 Troubleshooting

### Problema: Muitos requests 304

**Causa**: Cache funcionando, mas navegador ainda valida
**Solução**: Já implementado com `immutable`

### Problema: Latência entre segmentos

**Causa**: Prefetch não está funcionando
**Solução**: Verificar console do navegador

### Problema: Requests duplicados

**Causa**: React re-renderizando componente
**Solução**: Verificar `useEffect` dependencies

## 📚 Referências

- [Nginx MP4 Module](http://nginx.org/en/docs/http/ngx_http_mp4_module.html)
- [HTTP Caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching)
- [Resource Hints (Prefetch)](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/prefetch)
- [Range Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Range_requests)

## ✅ Checklist de Validação

- [x] Cache configurado no Nginx
- [x] Prefetch implementado no frontend
- [x] Range requests funcionando
- [x] CORS configurado
- [ ] Autenticação implementada (FASE 2)
- [ ] Métricas de cache coletadas
- [ ] Testes de carga validados

---

**Última atualização**: 2025-01-XX
**Status**: ✅ Otimizado para desenvolvimento local
