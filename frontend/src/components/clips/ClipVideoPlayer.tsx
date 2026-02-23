import { useEffect, useRef } from 'react'
import Hls from 'hls.js'

interface ClipVideoPlayerProps {
  hlsUrl: string
  className?: string
}

export function ClipVideoPlayer({ hlsUrl, className = '' }: ClipVideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const hlsRef = useRef<Hls | null>(null)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    if (Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: false,
        backBufferLength: 90,
        maxBufferLength: 300,
        maxMaxBufferLength: 600,
        liveSyncDurationCount: 3,
        liveMaxLatencyDurationCount: 10,
      })

      hls.loadSource(hlsUrl)
      hls.attachMedia(video)

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch(console.error)
      })

      hls.on(Hls.Events.ERROR, (event, data) => {
        console.error('HLS Error:', data)
      })

      hlsRef.current = hls

      return () => {
        hls.destroy()
      }
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = hlsUrl
      video.addEventListener('loadedmetadata', () => {
        video.play().catch(console.error)
      })
    }
  }, [hlsUrl])

  return (
    <video
      ref={videoRef}
      controls
      className={className}
      style={{ width: '100%', height: '100%' }}
    />
  )
}
