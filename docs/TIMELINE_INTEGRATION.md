# Timeline Integrada no Modal da Câmera

## O que foi feito

Integrei a `PlaybackTimeline` no `CameraDetailModal` **SEM TOCAR NO VideoPlayer**.

## Estrutura Visual

```
┌─────────────────────────────────────┐
│  Header (nome, localização, X)     │
├─────────────────────────────────────┤
│                                     │
│         VideoPlayer                 │  ← INTOCADO
│         (aspect-video)              │
│                                     │
│  [Botão "Ao Vivo"] (se playback)   │
├─────────────────────────────────────┤
│     PlaybackTimeline (NOVO)        │  ← Adicionado aqui
│  [24h][1h][5min] ◀ 14:35:00 ▶      │
│  ████████░░░░░░░░████████           │
│         ▲ (playhead)                │
├─────────────────────────────────────┤
│  Info (status, id, data, stream)   │
└─────────────────────────────────────┘
```

## Como Funciona

### Modo Live (padrão)
```typescript
mode = 'live'
videoSrc = "/streaming/cameras/1/index.m3u8"
```

- Timeline mostra tempo atual
- Botão "Ao Vivo" oculto
- Player toca stream ao vivo

### Modo Playback (usuário clica na timeline)

1. Usuário clica na timeline às 14:35
2. `handleSeek(time)` é chamado
3. Muda para `mode = 'playback'`
4. Calcula novo src: `/playback/camera/1/2026-02-05/14-35.m3u8`
5. Atualiza `videoSrc`
6. VideoPlayer re-renderiza com novo src
7. Botão "Ao Vivo" aparece no canto superior direito

### Voltar ao Vivo

1. Usuário clica botão "Ao Vivo"
2. `goLive()` é chamado
3. Restaura `videoSrc` para HLS live
4. Muda para `mode = 'live'`
5. Botão desaparece

## Código Adicionado

### Estado do Modal
```typescript
const [mode, setMode] = useState<'live' | 'playback'>('live')
const [playbackTime, setPlaybackTime] = useState(new Date())
const [videoSrc, setVideoSrc] = useState(streamingService.getHlsUrl(camera.id))
```

### Handler de Seek
```typescript
const handleSeek = (time: Date) => {
  setMode('playback')
  setPlaybackTime(time)
  
  const dateStr = time.toISOString().split('T')[0]
  const timeStr = `${String(time.getHours()).padStart(2, '0')}-${String(time.getMinutes()).padStart(2, '0')}`
  const playbackUrl = `/playback/camera/${camera.id}/${dateStr}/${timeStr}.m3u8`
  
  setVideoSrc(playbackUrl)
}
```

### Botão Ao Vivo
```typescript
{mode === 'playback' && (
  <button onClick={goLive} className="absolute top-4 right-4 ...">
    <Radio className="w-4 h-4" />
    Ao Vivo
  </button>
)}
```

### Timeline
```typescript
<PlaybackTimeline
  cameraId={camera.id}
  currentTime={mode === 'live' ? new Date() : playbackTime}
  recordings={recordings}
  onSeek={handleSeek}
/>
```

## O que o VideoPlayer NÃO sabe

- Que existe uma timeline
- Se está em live ou playback
- Que o src mudou de live para histórico

**Ele só toca HLS. Sempre.**

## Gravações (Mock)

Atualmente usando dados mock:
```typescript
const recordings = [
  {
    start: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2h atrás
    end: new Date(Date.now() - 1 * 60 * 60 * 1000),   // 1h atrás
    type: 'continuous'
  },
  {
    start: new Date(Date.now() - 30 * 60 * 1000),     // 30min atrás
    end: new Date(),                                   // agora
    type: 'continuous'
  }
]
```

### Próximo Passo: API Real

Criar endpoint:
```
GET /api/cameras/{id}/recordings?date={date}
```

Retorna:
```json
[
  {
    "start": "2026-02-05T12:00:00Z",
    "end": "2026-02-05T14:30:00Z",
    "type": "continuous"
  }
]
```

## Backend Necessário

### Endpoint de Playback HLS

```
GET /playback/camera/{id}/{date}/{time}.m3u8
```

Exemplo:
```
/playback/camera/1/2026-02-05/14-35.m3u8
```

Deve retornar:
- Manifest HLS (.m3u8)
- Apontando para segmentos (.ts) daquele horário
- Gerado on-demand ou pré-processado

### Implementação Sugerida

1. Buscar gravação que contém o timestamp
2. Calcular offset no arquivo MP4
3. Gerar manifest HLS com ffmpeg:
```bash
ffmpeg -ss 14:35:00 -i recording.mp4 -t 300 -c copy -f hls output.m3u8
```

## Funcionalidades Implementadas

- ✅ Timeline visual com canvas
- ✅ Segmentos de gravação (barras azuis)
- ✅ Playhead (linha vermelha)
- ✅ Zoom temporal (24h/1h/5min)
- ✅ Navegação com setas
- ✅ Seek por clique
- ✅ Botão "Ao Vivo"
- ✅ Troca de src sem tocar no player
- ✅ Timestamp atual exibido

## Testes

1. Abrir modal de câmera → deve mostrar live + timeline
2. Clicar na timeline → deve aparecer botão "Ao Vivo"
3. Console deve mostrar: `/playback/camera/1/...`
4. Clicar "Ao Vivo" → deve voltar ao live
5. Trocar zoom → timeline deve ajustar
6. Navegar com setas → view deve mover

## Vantagens

- VideoPlayer intocado (seguro)
- Fácil reverter se necessário
- Timeline isolada (testável)
- Backend pode ser implementado depois
- Funciona com mock data agora

## Próximos Passos

1. Implementar backend de playback HLS
2. Criar API de gravações
3. Substituir mock por dados reais
4. Adicionar eventos de IA na timeline
5. Implementar exportação de clipes
