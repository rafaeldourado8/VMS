import { useEffect, useRef, useState } from 'react'
import { cn } from '@/lib/utils'
import { ChevronLeft, ChevronRight, Download } from 'lucide-react'
import { Button } from '@/components/ui'

type TimeScale = '24h' | '1h' | '5m'

interface RecordingSegment {
  start: Date
  end: Date
  type: 'continuous' | 'event' | 'manual'
}

interface PlaybackTimelineProps {
  cameraId: number
  currentTime: Date
  recordings: RecordingSegment[]
  onSeek: (time: Date) => void
  onExport?: (start: Date, end: Date) => void
  className?: string
  startTime?: Date // Tempo de início da timeline
}

export function PlaybackTimeline({
  cameraId,
  currentTime,
  recordings,
  onSeek,
  onExport,
  className,
  startTime = new Date()
}: PlaybackTimelineProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [scale, setScale] = useState<TimeScale>('5m')
  const [isDragging, setIsDragging] = useState(false)
  const [viewStart, setViewStart] = useState<Date | null>(null)
  const hasInitialized = useRef(false)
  
  // Calcula duração desde o início da timeline
  const getElapsedMinutes = () => {
    return Math.floor((new Date().getTime() - startTime.getTime()) / 60000)
  }
  
  // Define escala automática baseada no tempo decorrido
  const getAutoScale = (): TimeScale => {
    const elapsed = getElapsedMinutes()
    if (elapsed <= 5) return '5m'
    if (elapsed <= 60) return '1h'
    return '24h'
  }
  
  // Atualiza escala automaticamente
  useEffect(() => {
    const autoScale = getAutoScale()
    setScale(autoScale)
  }, [currentTime])
  
  // Inicializa viewStart no startTime
  useEffect(() => {
    if (!hasInitialized.current) {
      setViewStart(new Date(startTime.getTime()))
      hasInitialized.current = true
    }
  }, [])
  
  // Fallback
  const effectiveViewStart = viewStart || startTime

  const scaleMinutes = { '24h': 1440, '1h': 60, '5m': 5 }[scale]

  useEffect(() => {
    drawTimeline()
  }, [recordings, currentTime, effectiveViewStart, scale])

  const drawTimeline = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const { width, height } = canvas
    ctx.clearRect(0, 0, width, height)

    // Background
    ctx.fillStyle = '#1a1a1a'
    ctx.fillRect(0, 0, width, height)

    // Recording segments
    const viewEnd = new Date(effectiveViewStart.getTime() + scaleMinutes * 60 * 1000)
    const pixelPerMs = width / (viewEnd.getTime() - effectiveViewStart.getTime())

    recordings.forEach(seg => {
      if (seg.end < effectiveViewStart || seg.start > viewEnd) return

      const x1 = Math.max(0, (seg.start.getTime() - effectiveViewStart.getTime()) * pixelPerMs)
      const x2 = Math.min(width, (seg.end.getTime() - effectiveViewStart.getTime()) * pixelPerMs)

      ctx.fillStyle = seg.type === 'event' ? '#ef4444' : seg.type === 'manual' ? '#eab308' : '#3b82f6'
      ctx.fillRect(x1, height * 0.4, x2 - x1, height * 0.2)
    })

    // Time markers
    ctx.strokeStyle = '#404040'
    ctx.fillStyle = '#888'
    ctx.font = '10px sans-serif'
    
    const markerInterval = scale === '24h' ? 3600000 : scale === '1h' ? 300000 : 60000
    let markerTime = Math.ceil(effectiveViewStart.getTime() / markerInterval) * markerInterval

    while (markerTime < viewEnd.getTime()) {
      const x = (markerTime - effectiveViewStart.getTime()) * pixelPerMs
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height)
      ctx.stroke()

      const date = new Date(markerTime)
      const label = scale === '24h' 
        ? `${date.getHours()}:00`
        : `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
      
      ctx.fillText(label, x + 2, 12)
      markerTime += markerInterval
    }

    // Playhead
    const playheadX = (currentTime.getTime() - effectiveViewStart.getTime()) * pixelPerMs
    if (playheadX >= 0 && playheadX <= width) {
      ctx.strokeStyle = '#ef4444'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.moveTo(playheadX, 0)
      ctx.lineTo(playheadX, height)
      ctx.stroke()
      ctx.lineWidth = 1
    }
  }

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const ratio = x / rect.width

    const viewEnd = new Date(effectiveViewStart.getTime() + scaleMinutes * 60 * 1000)
    const clickedTime = new Date(effectiveViewStart.getTime() + ratio * (viewEnd.getTime() - effectiveViewStart.getTime()))

    onSeek(clickedTime)
  }

  const shift = (minutes: number) => {
    setViewStart(new Date((viewStart || effectiveViewStart).getTime() + minutes * 60 * 1000))
  }

  return (
    <div className={cn('flex flex-col gap-2 bg-background p-3 rounded-lg border', className)}>
      <div className="flex items-center justify-between">
        <div className="flex gap-1">
          <Button
            variant={scale === '24h' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setScale('24h')}
            disabled={getElapsedMinutes() < 60}
          >
            24h
          </Button>
          <Button
            variant={scale === '1h' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setScale('1h')}
            disabled={getElapsedMinutes() < 5}
          >
            1h
          </Button>
          <Button
            variant={scale === '5m' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setScale('5m')}
          >
            5min
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={() => shift(-scaleMinutes / 2)}>
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <span className="text-sm font-mono">
            {currentTime.toLocaleTimeString()}
          </span>
          <span className="text-xs text-muted-foreground">
            ({getElapsedMinutes()}min)
          </span>
          <Button variant="ghost" size="icon" onClick={() => shift(scaleMinutes / 2)}>
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>

        {onExport && (
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
        )}
      </div>

      <canvas
        ref={canvasRef}
        width={800}
        height={60}
        className="w-full h-[60px] cursor-pointer rounded"
        onClick={handleCanvasClick}
      />
    </div>
  )
}
