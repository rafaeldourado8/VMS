# Migração: HLS (.ts) → MP4 Direto

## Mudança

Removido sistema HLS com segmentos `.ts` e adotado streaming direto de arquivos `.mp4` via nginx.

## Arquitetura Nova

```
Frontend → Nginx (/recordings/) → MP4 files
```

### Nginx

- **Módulo mp4**: Habilita pseudo-streaming e seek eficiente
- **Chunked transfer**: Envia dados progressivamente
- **Range requests**: Suporta seek no player HTML5
- **AIO threads**: I/O assíncrono para performance

```nginx
location /recordings/ {
    alias /recordings/;
    
    mp4;
    mp4_buffer_size 1m;
    mp4_max_buffer_size 5m;
    
    add_header Accept-Ranges bytes;
    sendfile on;
    aio threads;
    directio 512;
}
```

### Frontend

- **Player nativo HTML5**: Sem dependência de HLS.js
- **Navegação entre blocos**: Troca automática de arquivo ao terminar
- **Seek inteligente**: Calcula qual bloco carregar baseado no timestamp

```typescript
const currentVideoUrl = `/recordings/camera_${cameraId}/${date}/${filename}.mp4`
```

## Benefícios

1. **Simplicidade**: Sem transcodificação HLS
2. **Performance**: Nginx serve MP4 nativamente
3. **Compatibilidade**: Funciona em todos navegadores modernos
4. **Seek rápido**: Módulo mp4 do nginx otimiza busca
5. **Menos overhead**: Sem geração de playlists .m3u8

## Estrutura de Arquivos

```
/recordings/
  camera_1/
    2026-02-25/
      10-30-00.mp4  (1 minuto)
      10-31-00.mp4  (1 minuto)
      10-32-00.mp4  (1 minuto)
```

## API Changes

### recordingService

```typescript
getRecordingUrl(cameraId: number, date: string, filename: string): string {
  return `/recordings/camera_${cameraId}/${date}/${filename}`
}
```

## Removido

- ❌ VOD Service (HLS playlist generator)
- ❌ HLS.js dependency
- ❌ Segmentos .ts
- ❌ Playlists .m3u8
- ❌ FFmpeg transcoding para HLS

## Mantido

- ✅ HLS para live streaming (MediaMTX)
- ✅ Timeline com blocos
- ✅ Clip creation
- ✅ Seek e navegação
