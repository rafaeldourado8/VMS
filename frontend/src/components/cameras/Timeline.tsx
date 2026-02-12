import { useState, useEffect, useRef } from 'react'
import { VideoPlayer } from './VideoPlayer'
import { Button } from '@/components/ui'
import { Calendar, Clock, Play } from 'lucide-react'
import api from '@/services/api'

interface TimelineProps {
  cameraId: number
  initialMode?: 'live' | 'playback'
}

interface Segment {
  start: string
  file: string
  size_mb: number
}

export function Timeline({ cameraId, initialMode = 'live' }: TimelineProps) {
  const [mode, setMode] = useState<'live' | 'playback'>(initialMode)
  const [date, setDate] = useState(new Date().toISOString().split('T')[0])
  const [segments, setSegments] = useState<Segment[]>([])
  const [currentUrl, setCurrentUrl] = useState(`/hls/cam_${cameraId}/index.m3u8`)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    if (mode === 'playback') {
      fetchTimeline()
    }
  }, [mode, date])

  const fetchTimeline = async () => {
    try {
      const { data } = await api.get(`/cameras/${cameraId}/timeline/?date=${date}`)
      setSegments(data.segments || [])
    } catch (err) {
      console.error('Failed to fetch timeline:', err)
      setSegments([])
    }
  }

  const switchToLive = () => {
    setMode('live')
    setCurrentUrl(`/hls/cam_${cameraId}/index.m3u8`)
  }

  const switchToPlayback = (segment: Segment) => {
    setMode('playback')
    setCurrentUrl(`/api/recordings/${cameraId}/${date}/${segment.file}`)
  }

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = Math.floor(seconds % 60)
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }

  return (
    <div className="flex flex-col h-full">
      {/* Player */}
      <div className="flex-1 relative">
        <VideoPlayer 
          src={currentUrl} 
          cameraId={cameraId}
          autoPlay 
          muted 
          onTimeUpdate={(time) => setCurrentTime(time)}
          onDurationChange={(dur) => setDuration(dur)}
        />
      </div>

      {/* Timeline Progress Bar */}
      {mode === 'playback' && duration > 0 && (
        <div className="px-4 py-2 bg-background">
          <div className="relative h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="absolute h-full bg-blue-600 transition-all duration-200"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="p-4 bg-background border-t">
        <div className="flex gap-2 mb-4">
          <Button
            variant={mode === 'live' ? 'default' : 'outline'}
            onClick={switchToLive}
          >
            <Play className="w-4 h-4 mr-2" />
            Ao Vivo
          </Button>
          <Button
            variant={mode === 'playback' ? 'default' : 'outline'}
            onClick={() => setMode('playback')}
          >
            <Clock className="w-4 h-4 mr-2" />
            Gravações
          </Button>
        </div>

        {mode === 'playback' && (
          <>
            <label htmlFor="timeline-date" className="block text-sm font-medium mb-1">
              <Calendar className="w-4 h-4 inline mr-1" />
              Data
            </label>
            <input
              id="timeline-date"
              name="timeline-date"
              type="date"
              value={date}
              max={new Date().toISOString().split('T')[0]}
              onChange={(e) => setDate(e.target.value)}
              className="mb-2 px-3 py-2 border rounded w-full"
            />
            {segments.length > 0 ? (
              <div className="flex gap-2 overflow-x-auto">
                {segments.map((seg) => (
                  <Button
                    key={seg.start}
                    variant="outline"
                    size="sm"
                    onClick={() => switchToPlayback(seg)}
                  >
                    {seg.start}
                  </Button>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Nenhuma gravação disponível para esta data</p>
            )}
          </>
        )}
      </div>
    </div>
  )
}
