# Otimização HLS - Chunks de 5s

## Problema
- Arquivos MP4 de 60s (~34MB) causavam travamentos no navegador
- Alto consumo de banda ao carregar segmentos inteiros
- Experiência ruim ao navegar na timeline

## Solução Implementada

### Fatiamento Dinâmico
O serviço VOD agora divide cada MP4 de 60s em **12 chunks virtuais de 5s**:

```
10-30-00.mp4 (60s, 34MB)
  ↓
10-30-00_0.ts  (0-5s,   ~2.8MB)
10-30-00_1.ts  (5-10s,  ~2.8MB)
10-30-00_2.ts  (10-15s, ~2.8MB)
...
10-30-00_11.ts (55-60s, ~2.8MB)
```

### Como Funciona

1. **Playlist (index.m3u8)**
   - `#EXT-X-TARGETDURATION:5` (antes era 60)
   - Cada MP4 gera 12 entradas de 5s
   - Total: ~720 chunks por hora

2. **Endpoint de Segmento**
   - Recebe: `/vod/segment/{camera_id}/{date}/10-30-00_5.ts`
   - Extrai: segundos 25-30 do arquivo 10-30-00.mp4
   - Usa: `ffmpeg -ss 25 -t 5 -c:v copy`

3. **Streaming On-the-Fly**
   - Sem cache em disco
   - Transmuxing MP4→TS em memória
   - Latência: ~200ms por chunk

## Benefícios

✅ **Banda reduzida**: 2.8MB vs 34MB por segmento
✅ **Navegação rápida**: Seek instantâneo na timeline
✅ **Sem travamentos**: Navegador processa chunks pequenos
✅ **Disco eficiente**: Continua gravando em 60s

## Exemplo de Uso

```javascript
// Frontend carrega playlist
const url = '/vod/playlist/1/2026-02-24/index.m3u8'

// Player HLS.js baixa apenas chunks necessários
// Usuário clica em 10:30:25 → baixa apenas 10-30-00_5.ts (2.8MB)
```

## Testes

```bash
# Reiniciar serviço VOD
docker-compose restart vod

# Testar playlist
curl http://localhost/vod/playlist/1/2026-02-24/index.m3u8

# Testar chunk específico
curl http://localhost/vod/segment/1/2026-02-24/10-30-00_5.ts -o test.ts
```

## Monitoramento

```bash
# Logs do VOD
docker-compose logs -f vod

# Verificar uso de CPU/memória
docker stats vod
```

## Notas Técnicas

- FFmpeg usa `-ss` (seek) antes de `-i` para fast seek
- `-c:v copy` evita re-encode (apenas remux)
- `-copyts` mantém timestamps originais
- Chunks são gerados sob demanda (zero cache)
