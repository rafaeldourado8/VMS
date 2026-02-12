import { useState } from 'react'
import { VideoPlayer } from './VideoPlayer'
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
  const [videoSrc, setVideoSrc] = useState(liveUrl)

  const goLive = () => {
    setMode('live')
    setVideoSrc(liveUrl)
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
    </div>
  )
}
