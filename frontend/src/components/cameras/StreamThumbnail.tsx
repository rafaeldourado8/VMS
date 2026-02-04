import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'
import { Camera, Play } from 'lucide-react'

interface StreamThumbnailProps {
  cameraId: number
  cameraName?: string
  cameraStatus?: string
  className?: string
  onClick?: () => void
  showStatus?: boolean
}

export function StreamThumbnail({ 
  cameraId,
  cameraName,
  cameraStatus = 'offline',
  className, 
  onClick, 
  showStatus = true
}: StreamThumbnailProps) {
  const [snapshot, setSnapshot] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const isOnline = cameraStatus === 'online'

  useEffect(() => {
    const cacheKey = `camera_snapshot_${cameraId}`
    const cached = localStorage.getItem(cacheKey)
    
    if (cached) {
      setSnapshot(cached)
      setIsLoading(false)
      return
    }

    const loadSnapshot = async () => {
      try {
        const response = await fetch(`/streaming/cameras/${cameraId}/snapshot`)
        
        if (response.ok) {
          const blob = await response.blob()
          const reader = new FileReader()
          reader.onloadend = () => {
            const base64 = reader.result as string
            setSnapshot(base64)
            localStorage.setItem(cacheKey, base64)
          }
          reader.readAsDataURL(blob)
        } else {
          setError('Sem snapshot')
        }
      } catch (err) {
        setError('Sem snapshot')
      } finally {
        setIsLoading(false)
      }
    }

    loadSnapshot()
  }, [cameraId])

  return (
    <div 
      className={cn(
        "relative aspect-video bg-black rounded-lg overflow-hidden cursor-pointer group",
        className
      )}
      onClick={onClick}
    >
      {snapshot && (
        <img
          src={snapshot}
          alt={cameraName}
          className="w-full h-full object-cover"
        />
      )}

      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {error && !snapshot && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80">
          <Camera className="w-8 h-8 text-gray-400 mb-2" />
          <span className="text-xs text-gray-400">{error}</span>
        </div>
      )}

      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
        <Play className="w-8 h-8 text-white" />
      </div>

      {showStatus && (
        <div className="absolute top-2 right-2">
          <div className={cn(
            "w-2 h-2 rounded-full",
            isOnline ? "bg-green-500" : "bg-red-500"
          )} />
        </div>
      )}

      {cameraName && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2">
          <span className="text-xs text-white truncate block">{cameraName}</span>
        </div>
      )}
    </div>
  )
}