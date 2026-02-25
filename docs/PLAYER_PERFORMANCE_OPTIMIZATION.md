# Otimizações de Performance - Timeline Player

## Problema
- 182 requisições carregando 370KB
- Player travando ao carregar playlist completa do dia
- Chunks de 5s gerando muitas requisições

## Otimizações Implementadas

### 1. Redução de Buffer (HLS.js)

**Antes:**
```javascript
maxBufferLength: 180,      // 180s = 36 chunks
maxMaxBufferLength: 600,   // 600s = 120 chunks
backBufferLength: 90       // 90s atrás
```

**Depois:**
```javascript
maxBufferLength: 30,       // 30s = 6 chunks apenas
maxMaxBufferLength: 60,    // 60s máximo
backBufferLength: 10       // 10s atrás
maxBufferSize: 10MB        // Limite de memória
```

**Resultado:** ~6 requisições iniciais vs 36

### 2. Filtro de Hora na Playlist (Opcional)

Playlist pode ser filtrada por hora:
```
/vod/playlist/1/2026-02-24/index.m3u8?start_hour=10&end_hour=12
```

Reduz playlist de 24h (17.280 chunks) para 2h (1.440 chunks)

### 3. Lazy Loading

HLS.js agora carrega chunks sob demanda:
- Inicial: 6 chunks (~15MB)
- Seek: 6 chunks da nova posição
- Playback: 1 chunk a cada 5s

## Métricas Esperadas

| Métrica | Antes | Depois |
|---------|-------|--------|
| Requisições iniciais | 182 | ~10 |
| Dados iniciais | 370KB | ~50KB |
| Buffer inicial | 180s | 30s |
| Tempo para play | 3-5s | <1s |

## Uso

### Frontend (automático)
```typescript
// HLS.js configurado automaticamente
// Carrega apenas 30s de buffer
```

### Backend (filtro opcional)
```bash
# Playlist completa (24h)
GET /vod/playlist/1/2026-02-24/index.m3u8

# Playlist filtrada (10h-12h)
GET /vod/playlist/1/2026-02-24/index.m3u8?start_hour=10&end_hour=12
```

## Testes

```bash
# Reiniciar serviços
docker-compose restart vod

# Monitorar requisições
# Abrir DevTools > Network
# Filtrar por ".ts"
# Deve mostrar ~6 requisições iniciais
```

## Próximas Otimizações (se necessário)

1. **Adaptive Bitrate**: Reduzir qualidade em conexões lentas
2. **Preload Inteligente**: Carregar próximos chunks baseado em padrão de uso
3. **Cache CDN**: Cachear chunks mais acessados
4. **Compressão**: Gzip/Brotli nos segmentos TS
