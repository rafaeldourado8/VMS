import { useState } from 'react'
import { VideoPlayer } from './VideoPlayer'
import { PlaybackTimeline } from './PlaybackTimeline'
import { Button } from '@/components/ui'
import { Radio } from 'lucide-react'

interface CameraViewerProps {
  cameraId: number
  cameraName?: string
  liveUrl: string
  className?: string
}

export function CameraViewer({ cameraId, cameraName, liveUrl, className }: CameraViewerProps) {
  const [mode, setMode] = useState<'live' | 'playback'>('live')
  const [playbackTime, setPlaybackTime] = useState(new Date())
  const [videoSrc, setVideoSrc] = useState(liveUrl)

  // Mock recordings - substituir por API real
  const recordings = [
    {
      start: new Date(Date.now() - 2 * 60 * 60 * 1000),
      end: new Date(Date.now() - 1 * 60 * 60 * 1000),
      type: 'continuous' as const
    },
    {
      start: new Date(Date.now() - 30 * 60 * 1000),
      end: new Date(),
      type: 'continuous' as const
    }
  ]

  const handleSeek = (time: Date) => {
    setMode('playback')
    setPlaybackTime(time)
    
    // Formato: /playback/camera/{id}/{YYYY-MM-DD}/{HH-mm}.m3u8
    const dateStr = time.toISOString().split('T')[0]
    const timeStr = `${String(time.getHours()).padStart(2, '0')}-${String(time.getMinutes()).padStart(2, '0')}`
    const playbackUrl = `/playback/camera/${cameraId}/${dateStr}/${timeStr}.m3u8`
    
    setVideoSrc(playbackUrl)
  }

  const goLive = () => {
    setMode('live')
    setVideoSrc(liveUrl)
    setPlaybackTime(new Date())
  }

  return (
    <div className={className}>
      <div className="relative">
        <VideoPlayer
          src={videoSrc}
          autoPlay
          muted
          className="w-full aspect-video"
        />
        
        {mode === 'playback' && (
          <Button
            variant="destructive"
            size="sm"
            className="absolute top-4 right-4"
            onClick={goLive}
          >
            <Radio className="w-4 h-4 mr-2" />
            Ao Vivo
          </Button>
        )}
      </div>

      <PlaybackTimeline
        cameraId={cameraId}
        currentTime={mode === 'live' ? new Date() : playbackTime}
        recordings={recordings}
        onSeek={handleSeek}
        className="mt-2"
      />
    </div>
  )
}
