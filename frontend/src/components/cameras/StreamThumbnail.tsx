import { useEffect, useRef, useState } from 'react'
import Hls from 'hls.js'
import { cn } from '@/lib/utils'
import { AlertCircle, Play, Camera } from 'lucide-react'

interface StreamThumbnailProps {
  src: string
  fallbackSrc?: string
  className?: string
  onClick?: () => void
  showStatus?: boolean
  cameraName?: string
}

// Cache global de snapshots por src
const snapshotCache = new Map<string, string>()

export function StreamThumbnail({ 
  src, 
  fallbackSrc,
  className, 
  onClick, 
  showStatus = true,
  cameraName 
}: StreamThumbnailProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imgRef = useRef<HTMLImageElement>(null)
  const hlsRef = useRef<Hls | null>(null)
  const snapshotTimerRef = useRef<NodeJS.Timeout | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isOnline, setIsOnline] = useState(false)
  const [snapshot, setSnapshot] = useState<string | null>(() => snapshotCache.get(src) || null)
  const [isVisible, setIsVisible] = useState(false)

  // Intersection Observer para detectar quando está visível
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting)
      },
      { threshold: 0.1 }
    )

    if (containerRef.current) {
      observer.observe(containerRef.current)
    }

    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    // Se já tem snapshot em cache, usa ele
    if (snapshotCache.has(src)) {
      setSnapshot(snapshotCache.get(src)!)
      setIsLoading(false)
      setIsOnline(true)
      return
    }

    if (!isVisible) return

    const video = videoRef.current
    const canvas = canvasRef.current
    if (!video || !canvas || !src) return

    setIsLoading(true)
    setError(null)

    if (src.includes('.m3u8')) {
      if (Hls.isSupported()) {
        const hls = new Hls({
          enableWorker: false,
          lowLatencyMode: false,
          maxBufferLength: 5,
          maxBufferSize: 5 * 1000 * 1000,
        })

        hls.loadSource(src)
        hls.attachMedia(video)

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          setIsLoading(false)
          setIsOnline(true)
          video.play().catch(() => {})

          // Após 5 segundos, captura screenshot e para o streaming
          snapshotTimerRef.current = setTimeout(() => {
            const ctx = canvas.getContext('2d')
            if (ctx && video.videoWidth > 0) {
              canvas.width = video.videoWidth
              canvas.height = video.videoHeight
              ctx.drawImage(video, 0, 0)
              const dataUrl = canvas.toDataURL('image/jpeg', 0.8)
              setSnapshot(dataUrl)
              snapshotCache.set(src, dataUrl)
              hls.destroy()
            }
          }, 5000)
        })

        hls.on(Hls.Events.ERROR, (_, data) => {
          if (data.fatal) {
            setIsOnline(false)
            snapshotCache.delete(src)
            if (fallbackSrc) {
              setIsLoading(false)
            } else {
              setError('Offline')
              setIsLoading(false)
            }
          }
        })

        hlsRef.current = hls

        return () => {
          if (snapshotTimerRef.current) clearTimeout(snapshotTimerRef.current)
          hls.destroy()
        }
      }
    }

    video.addEventListener('error', () => {
      setIsOnline(false)
      snapshotCache.delete(src)
      if (fallbackSrc) {
        setIsLoading(false)
      } else {
        setError('Offline')
        setIsLoading(false)
      }
    })

  }, [src, fallbackSrc, isVisible])

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative aspect-video bg-black rounded-lg overflow-hidden cursor-pointer group",
        className
      )}
      onClick={onClick}
    >
      {snapshot ? (
        <img
          ref={imgRef}
          src={snapshot}
          alt={cameraName}
          className="w-full h-full object-cover"
          onError={() => {
            snapshotCache.delete(src)
            setSnapshot(null)
            setError('Offline')
          }}
        />
      ) : fallbackSrc && !isLoading ? (
        <img
          src={fallbackSrc}
          alt={cameraName}
          className="w-full h-full object-cover"
        />
      ) : (
        <video
          ref={videoRef}
          className="w-full h-full object-cover"
          muted
          playsInline
          autoPlay
        />
      )}
      <canvas ref={canvasRef} className="hidden" />

      {/* Loading */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* Error/Offline */}
      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80">
          <Camera className="w-8 h-8 text-gray-400 mb-2" />
          <span className="text-xs text-gray-400">{error}</span>
        </div>
      )}

      {/* Play overlay on hover */}
      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
        <Play className="w-8 h-8 text-white" />
      </div>

      {/* Status indicator */}
      {showStatus && (
        <div className="absolute top-2 right-2">
          <div className={cn(
            "w-2 h-2 rounded-full",
            isOnline || snapshot ? "bg-green-500" : "bg-red-500"
          )} />
        </div>
      )}

      {/* Camera name */}
      {cameraName && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
          <span className="text-xs text-white truncate block">{cameraName}</span>
        </div>
      )}
    </div>
  )
}