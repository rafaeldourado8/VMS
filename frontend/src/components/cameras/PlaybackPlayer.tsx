import { useState, useRef, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronLeft, ChevronRight, Play, Pause } from 'lucide-react'
import { Button, Card, CardContent } from '@/components/ui'
import { recordingService } from '@/services/api'
import Hls from 'hls.js'

interface PlaybackPlayerProps {
  cameraId: number
  cameraName: string
}

export function PlaybackPlayer({ cameraId, cameraName }: PlaybackPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const hlsRef = useRef<Hls | null>(null)
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(86400) // 24h em segundos

  const { data: recordings } = useQuery({
    queryKey: ['recordings', cameraId, selectedDate],
    queryFn: () => recordingService.list({
      camera_id: cameraId,
      date: selectedDate,
    }),
  })

  const goToPreviousDay = () => {
    const date = new Date(selectedDate)
    date.setDate(date.getDate() - 1)
    setSelectedDate(date.toISOString().split('T')[0])
  }

  const goToNextDay = () => {
    const date = new Date(selectedDate)
    date.setDate(date.getDate() + 1)
    const today = new Date().toISOString().split('T')[0]
    if (date.toISOString().split('T')[0] <= today) {
      setSelectedDate(date.toISOString().split('T')[0])
    }
  }

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!recordings?.recordings?.length) return
    
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const percentage = x / rect.width
    const targetSeconds = percentage * 86400
    
    const closest = recordings.recordings.reduce((prev: any, curr: any) => {
      if (!prev.start_time || !curr.start_time) return prev
      
      const [ph, pm, ps] = prev.start_time.split(':').map(Number)
      const [ch, cm, cs] = curr.start_time.split(':').map(Number)
      const prevSeconds = ph * 3600 + pm * 60 + ps
      const currSeconds = ch * 3600 + cm * 60 + cs
      
      return Math.abs(currSeconds - targetSeconds) < Math.abs(prevSeconds - targetSeconds) ? curr : prev
    })
    
    if (closest?.filename) {
      loadRecording(closest.filename)
    }
  }

  const loadRecording = (filename: string) => {
    if (!videoRef.current) return

    const url = recordingService.getPlaybackUrl(cameraId, selectedDate, filename)
    
    if (hlsRef.current) {
      hlsRef.current.destroy()
      hlsRef.current = null
    }

    if (Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: false,
        backBufferLength: 90,
      })
      hls.loadSource(url)
      hls.attachMedia(videoRef.current)
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        videoRef.current?.play().catch(() => {})
      })
      hlsRef.current = hls
    } else if (videoRef.current.canPlayType('application/vnd.apple.mpegurl')) {
      videoRef.current.src = url
      videoRef.current.play().catch(() => {})
    }
  }

  const togglePlayPause = () => {
    if (!videoRef.current) return
    if (isPlaying) {
      videoRef.current.pause()
    } else {
      videoRef.current.play()
    }
    setIsPlaying(!isPlaying)
  }

  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`
  }

  useEffect(() => {
    if (recordings?.recordings?.length && videoRef.current && !hlsRef.current) {
      loadRecording(recordings.recordings[0].filename)
    }
  }, [recordings])

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleTimeUpdate = () => setCurrentTime(video.currentTime)
    const handleLoadedMetadata = () => setDuration(video.duration)

    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('loadedmetadata', handleLoadedMetadata)

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('loadedmetadata', handleLoadedMetadata)
      if (hlsRef.current) {
        hlsRef.current.destroy()
      }
    }
  }, [])

  return (
    <Card>
      <CardContent className="p-0">
        <div className="bg-black aspect-video">
          <video
            ref={videoRef}
            className="w-full h-full"
            controls={false}
          />
        </div>

        <div className="p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">{cameraName}</h3>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="icon" onClick={goToPreviousDay}>
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="text-sm font-mono min-w-[100px] text-center">
                {new Date(selectedDate).toLocaleDateString('pt-BR')}
              </span>
              <Button
                variant="outline"
                size="icon"
                onClick={goToNextDay}
                disabled={selectedDate === new Date().toISOString().split('T')[0]}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <div
              className="relative h-16 bg-secondary rounded cursor-pointer"
              onClick={handleTimelineClick}
            >
              {recordings?.recordings?.map((rec: any) => {
                if (!rec.start_time) return null
                const [h, m, s] = rec.start_time.split(':').map(Number)
                const startSeconds = h * 3600 + m * 60 + s
                const left = (startSeconds / 86400) * 100
                
                return (
                  <div
                    key={rec.filename}
                    className="absolute top-0 bottom-0 bg-primary/60 hover:bg-primary/80"
                    style={{
                      left: `${left}%`,
                      width: '0.5%',
                    }}
                  />
                )
              })}
              
              <div className="absolute inset-0 flex items-center justify-between px-2 text-xs text-muted-foreground pointer-events-none">
                {Array.from({ length: 25 }, (_, i) => (
                  <span key={i}>{i.toString().padStart(2, '0')}h</span>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Button variant="outline" size="icon" onClick={togglePlayPause}>
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              </Button>
              
              <div className="flex-1 text-sm text-muted-foreground">
                {recordings?.recordings.length || 0} gravações disponíveis
                {recordings?.total_size_mb && ` • ${recordings.total_size_mb} MB`}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
