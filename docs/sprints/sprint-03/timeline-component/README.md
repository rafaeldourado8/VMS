# 🎬 Timeline Component - Especificação Frontend

## 📋 Visão Geral

Componente React para reprodução de gravações com timeline interativa, controles de player e criação de clipes.

---

## 🎨 Interface

```tsx
<Timeline
  cameraId={1}
  cameraName="Entrada Principal"
  onClose={() => setShowTimeline(false)}
/>
```

---

## 🏗️ Estrutura

```
Timeline/
├── Timeline.tsx           # Container principal
├── VideoPlayer.tsx        # Player HLS
├── Controls.tsx           # Botões de controle
├── ProgressBar.tsx        # Barra de progresso
├── DateSelector.tsx       # Seletor de data
├── ClipCreator.tsx        # Interface de clipes
└── DetectionMarkers.tsx   # Marcadores de eventos
```

---

## 💻 Implementação

### Timeline.tsx
```tsx
export function Timeline({ cameraId, cameraName, onClose }: Props) {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(86400) // 24h
  
  const { data: recordings } = useQuery({
    queryKey: ['recordings', cameraId, currentDate],
    queryFn: () => api.get(`/recordings/${cameraId}/${format(currentDate, 'yyyy-MM-dd')}`)
  })
  
  return (
    <div className="fixed inset-0 z-50 bg-black">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-900">
        <h2 className="text-xl text-white">
          📹 {cameraName}
        </h2>
        <button onClick={onClose}>✕</button>
      </div>
      
      {/* Video Player */}
      <VideoPlayer
        src={recordings?.hls_url}
        onTimeUpdate={setCurrentTime}
        onDurationChange={setDuration}
        isPlaying={isPlaying}
      />
      
      {/* Controls */}
      <Controls
        isPlaying={isPlaying}
        onPlayPause={() => setIsPlaying(!isPlaying)}
        onSeek={(time) => setCurrentTime(time)}
      />
      
      {/* Progress Bar */}
      <ProgressBar
        currentTime={currentTime}
        duration={duration}
        onSeek={setCurrentTime}
        markers={recordings?.detections}
      />
      
      {/* Date Selector */}
      <DateSelector
        currentDate={currentDate}
        availableDays={recordings?.available_days}
        onDateChange={setCurrentDate}
      />
      
      {/* Clip Creator */}
      <ClipCreator
        cameraId={cameraId}
        currentTime={currentTime}
      />
    </div>
  )
}
```

### VideoPlayer.tsx
```tsx
export function VideoPlayer({ src, onTimeUpdate, isPlaying }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null)
  
  useEffect(() => {
    if (!videoRef.current) return
    
    const hls = new Hls()
    hls.loadSource(src)
    hls.attachMedia(videoRef.current)
    
    return () => hls.destroy()
  }, [src])
  
  useEffect(() => {
    if (!videoRef.current) return
    isPlaying ? videoRef.current.play() : videoRef.current.pause()
  }, [isPlaying])
  
  return (
    <video
      ref={videoRef}
      className="w-full h-[60vh] bg-black"
      onTimeUpdate={(e) => onTimeUpdate(e.currentTarget.currentTime)}
    />
  )
}
```

### ProgressBar.tsx
```tsx
export function ProgressBar({ currentTime, duration, onSeek, markers }: Props) {
  const progressPercent = (currentTime / duration) * 100
  
  return (
    <div className="relative h-12 bg-gray-800 px-4">
      {/* Timeline */}
      <div 
        className="h-2 bg-gray-700 rounded cursor-pointer"
        onClick={(e) => {
          const rect = e.currentTarget.getBoundingClientRect()
          const percent = (e.clientX - rect.left) / rect.width
          onSeek(percent * duration)
        }}
      >
        {/* Progress */}
        <div 
          className="h-full bg-blue-500 rounded"
          style={{ width: `${progressPercent}%` }}
        />
        
        {/* Detection Markers */}
        {markers?.map((marker, i) => (
          <div
            key={i}
            className="absolute top-0 w-1 h-2 bg-red-500"
            style={{ left: `${(marker.timestamp / duration) * 100}%` }}
            title={`Detecção: ${marker.plate}`}
          />
        ))}
      </div>
      
      {/* Time Labels */}
      <div className="flex justify-between text-xs text-gray-400 mt-1">
        <span>{formatTime(currentTime)}</span>
        <span>{formatTime(duration)}</span>
      </div>
    </div>
  )
}
```

### Controls.tsx
```tsx
export function Controls({ isPlaying, onPlayPause, onSeek }: Props) {
  return (
    <div className="flex items-center gap-4 p-4 bg-gray-900">
      {/* Skip Back */}
      <button onClick={() => onSeek(-10)}>
        ⏮️ -10s
      </button>
      
      {/* Play/Pause */}
      <button onClick={onPlayPause} className="text-2xl">
        {isPlaying ? '⏸️' : '▶️'}
      </button>
      
      {/* Skip Forward */}
      <button onClick={() => onSeek(10)}>
        ⏭️ +10s
      </button>
      
      {/* Volume */}
      <div className="flex items-center gap-2">
        🔊
        <input type="range" min="0" max="100" />
      </div>
      
      {/* Speed */}
      <select className="bg-gray-800 text-white">
        <option value="0.5">0.5x</option>
        <option value="1">1x</option>
        <option value="1.5">1.5x</option>
        <option value="2">2x</option>
      </select>
      
      {/* Fullscreen */}
      <button>⛶</button>
    </div>
  )
}
```

### DateSelector.tsx
```tsx
export function DateSelector({ currentDate, availableDays, onDateChange }: Props) {
  const plan = useAuthStore(state => state.user?.plan)
  const maxDays = { basic: 7, pro: 15, premium: 30 }[plan]
  
  return (
    <div className="flex items-center justify-between p-4 bg-gray-900">
      <button 
        onClick={() => onDateChange(subDays(currentDate, 1))}
        disabled={!canGoPrevious()}
      >
        ◀ Dia Anterior
      </button>
      
      <div className="text-center">
        <div className="text-white">
          📅 {format(currentDate, 'dd/MM/yyyy')}
        </div>
        <div className="text-sm text-gray-400">
          Dia {availableDays?.current} de {maxDays} disponíveis
        </div>
      </div>
      
      <button 
        onClick={() => onDateChange(addDays(currentDate, 1))}
        disabled={!canGoNext()}
      >
        Próximo Dia ▶
      </button>
    </div>
  )
}
```

### ClipCreator.tsx
```tsx
export function ClipCreator({ cameraId, currentTime }: Props) {
  const [clipStart, setClipStart] = useState<number>()
  const [clipEnd, setClipEnd] = useState<number>()
  const [isCreating, setIsCreating] = useState(false)
  
  const createClip = useMutation({
    mutationFn: (data) => api.post('/clips/', data),
    onSuccess: () => toast.success('Clipe criado!')
  })
  
  return (
    <div className="p-4 bg-gray-900 border-t border-gray-700">
      <div className="flex items-center gap-4">
        <button
          onClick={() => setClipStart(currentTime)}
          className="px-4 py-2 bg-blue-600 rounded"
        >
          ✂️ Marcar Início
        </button>
        
        {clipStart && (
          <button
            onClick={() => setClipEnd(currentTime)}
            className="px-4 py-2 bg-blue-600 rounded"
          >
            ✂️ Marcar Fim
          </button>
        )}
        
        {clipStart && clipEnd && (
          <button
            onClick={() => createClip.mutate({
              camera_id: cameraId,
              start_time: clipStart,
              end_time: clipEnd
            })}
            className="px-4 py-2 bg-green-600 rounded"
          >
            💾 Salvar Clipe ({formatDuration(clipEnd - clipStart)})
          </button>
        )}
        
        <button className="px-4 py-2 bg-gray-700 rounded">
          📋 Ver Clipes Salvos
        </button>
      </div>
    </div>
  )
}
```

---

## 🎯 Integração com Camera Grid

```tsx
// CameraCard.tsx
export function CameraCard({ camera }: Props) {
  const [showTimeline, setShowTimeline] = useState(false)
  
  return (
    <>
      <div 
        onDoubleClick={() => setShowTimeline(true)}
        className="cursor-pointer"
      >
        {/* Camera preview */}
      </div>
      
      {showTimeline && (
        <Timeline
          cameraId={camera.id}
          cameraName={camera.name}
          onClose={() => setShowTimeline(false)}
        />
      )}
    </>
  )
}
```

---

## 📦 Dependências

```json
{
  "dependencies": {
    "hls.js": "^1.4.0",
    "date-fns": "^2.30.0",
    "@tanstack/react-query": "^5.0.0"
  }
}
```

---

## 🧪 Testes

```tsx
describe('Timeline', () => {
  it('opens on double click', () => {
    render(<CameraCard camera={mockCamera} />)
    fireEvent.doubleClick(screen.getByRole('article'))
    expect(screen.getByText(/Timeline/)).toBeInTheDocument()
  })
  
  it('plays video on play button', () => {
    render(<Timeline {...props} />)
    fireEvent.click(screen.getByRole('button', { name: /play/i }))
    expect(mockVideo.play).toHaveBeenCalled()
  })
  
  it('creates clip with start and end', async () => {
    render(<Timeline {...props} />)
    fireEvent.click(screen.getByText(/Marcar Início/))
    fireEvent.click(screen.getByText(/Marcar Fim/))
    fireEvent.click(screen.getByText(/Salvar Clipe/))
    await waitFor(() => {
      expect(mockApi.post).toHaveBeenCalledWith('/clips/', expect.any(Object))
    })
  })
})
```

---

## 🎨 Estilos

- Fullscreen modal (z-50)
- Dark theme (bg-gray-900)
- Controles sempre visíveis
- Responsivo (mobile-friendly)
- Animações suaves (transition-all)

---

## ⚡ Performance

- Lazy load HLS.js
- Debounce seek operations
- Virtual scrolling para markers
- Memoize expensive calculations
- Cleanup on unmount
