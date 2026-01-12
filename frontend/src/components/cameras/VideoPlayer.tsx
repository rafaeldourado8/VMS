import { useEffect, useRef, useState } from 'react'
import Hls from 'hls.js'
import { Play, Pause, Volume2, VolumeX, Maximize, RefreshCw, AlertCircle, Scissors, Circle, Square } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui'
import { metricsClient } from '@/lib/metrics'
import { useVideoPlayer } from '@/hooks/useVideoPlayer'

interface VideoPlayerProps {
  src: string
  poster?: string
  autoPlay?: boolean
  muted?: boolean
  className?: string
  onError?: (error: string) => void
  onReady?: () => void
  showRecordingControls?: boolean
  cameraId?: number
  onProtocolSwitch?: (from: string, to: string) => void
}

export function VideoPlayer({
  src,
  poster,
  autoPlay = true,
  muted = true,
  className,
  onError,
  onReady,
  showRecordingControls = false,
  cameraId,
  onProtocolSwitch,
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const hlsRef = useRef<Hls | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const webrtcRetryTimer = useRef<NodeJS.Timeout | null>(null)
  
  const [isPlaying, setIsPlaying] = useState(autoPlay)
  const [isMuted, setIsMuted] = useState(muted)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showControls, setShowControls] = useState(false)
  const [retryCount, setRetryCount] = useState(0)
  const [isRecording, setIsRecording] = useState(false)
  const [recordingStartTime, setRecordingStartTime] = useState<Date | null>(null)
  const [showClipModal, setShowClipModal] = useState(false)
  const [protocol, setProtocol] = useState<'webrtc' | 'hls' | 'rtmp'>('hls')
  const maxRetries = 3

  const { 
    isStalled, 
    retryCount: stallRetryCount, 
    showError: showStallError, 
    manualRetry,
    setVolume: saveVolume 
  } = useVideoPlayer(videoRef, {
    onStalled: () => setError('Reconectando...'),
    onRecovery: () => setError(null),
    onError: (err) => setError(err)
  })

  const switchToHLS = () => {
    const prevProtocol = protocol
    setProtocol('hls')
    setError(null)
    onProtocolSwitch?.(prevProtocol, 'hls')
    
    if (cameraId) {
      metricsClient.recordProtocolFallback(cameraId, prevProtocol, 'hls')
    }
    
    // Retry WebRTC after 60s
    webrtcRetryTimer.current = setTimeout(() => {
      if (src.includes('webrtc') || src.includes('whip')) {
        setProtocol('webrtc')
      }
    }, 60000)
  }

  useEffect(() => {
    return () => {
      if (webrtcRetryTimer.current) clearTimeout(webrtcRetryTimer.current)
    }
  }, [])

  useEffect(() => {
    const video = videoRef.current
    if (!video || !src) return

    setIsLoading(true)
    setError(null)

    // Detect protocol
    const isWebRTC = src.includes('webrtc') || src.includes('whip')
    const isRTMP = src.includes('rtmp')
    const isHLS = src.includes('.m3u8')

    // Try WebRTC first if available
    if (isWebRTC && protocol === 'webrtc') {
      const timeout = setTimeout(() => {
        setError('WebRTC timeout')
        switchToHLS()
      }, 5000)

      // WebRTC connection logic would go here
      // For now, fallback to HLS
      clearTimeout(timeout)
      switchToHLS()
      return
    }

    // RTMP support
    if (isRTMP) {
      setProtocol('rtmp')
      video.src = src
      video.addEventListener('loadeddata', () => {
        setIsLoading(false)
        onReady?.()
      })
      return
    }

    // HLS
    if (isHLS || protocol === 'hls') {
      setProtocol('hls')
      if (Hls.isSupported()) {
        const hls = new Hls({
          enableWorker: true,
          lowLatencyMode: true,
          backBufferLength: 30,
          maxLoadingDelay: 4,
          maxBufferLength: 30,
          maxBufferSize: 60 * 1000 * 1000,
        })

        hls.loadSource(src)
        hls.attachMedia(video)

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          setIsLoading(false)
          if (autoPlay) {
            video.play().catch(() => {
              // Autoplay bloqueado, ok
            })
          }
          onReady?.()
        })

        hls.on(Hls.Events.ERROR, (_, data) => {
          console.log('HLS Error:', data)
          if (data.fatal) {
            switch (data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
                if (data.details === Hls.ErrorDetails.MANIFEST_LOAD_ERROR) {
                  setError('Câmera não está pronta. Aguarde...')
                } else {
                  setError('Erro de rede no stream')
                }
                break
              case Hls.ErrorTypes.MEDIA_ERROR:
                setError('Erro de mídia no stream')
                break
              default:
                setError('Stream indisponível')
                break
            }
            setIsLoading(false)
            onError?.(data.details || 'Stream error')
          }
        })

        hlsRef.current = hls

        return () => {
          hls.destroy()
        }
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        // Safari nativo
        video.src = src
        video.addEventListener('loadedmetadata', () => {
          setIsLoading(false)
          if (autoPlay) video.play()
          onReady?.()
        })
      }
    } else {
      // Video normal (não HLS)
      video.src = src
      video.addEventListener('loadeddata', () => {
        setIsLoading(false)
        onReady?.()
      })
    }

    video.addEventListener('error', () => {
      setError('Erro ao carregar vídeo')
      setIsLoading(false)
    })

  }, [src, autoPlay, onError, onReady])

  const togglePlay = () => {
    const video = videoRef.current
    if (!video) return

    if (video.paused) {
      video.play()
      setIsPlaying(true)
    } else {
      video.pause()
      setIsPlaying(false)
    }
  }

  const toggleMute = () => {
    const video = videoRef.current
    if (!video) return

    video.muted = !video.muted
    setIsMuted(video.muted)
    saveVolume(video.muted ? 0 : video.volume)
  }

  const toggleFullscreen = () => {
    const container = containerRef.current
    if (!container) return

    if (document.fullscreenElement) {
      document.exitFullscreen()
    } else {
      container.requestFullscreen()
    }
  }

  const retry = () => {
    setError(null)
    setIsLoading(true)
    setRetryCount(prev => prev + 1)
    
    if (hlsRef.current) {
      hlsRef.current.loadSource(src)
    } else if (videoRef.current) {
      videoRef.current.load()
    }
  }

  const toggleRecording = () => {
    if (isRecording) {
      // Parar gravação
      setIsRecording(false)
      setRecordingStartTime(null)
    } else {
      // Iniciar gravação
      setIsRecording(true)
      setRecordingStartTime(new Date())
    }
  }

  const createClip = () => {
    if (recordingStartTime) {
      setShowClipModal(true)
    }
  }

  // Auto retry para erros de manifest (câmera não ready)
  useEffect(() => {
    if (error && error.includes('não está pronta') && retryCount < maxRetries) {
      const timer = setTimeout(() => {
        retry()
      }, 3000) // Retry após 3 segundos
      
      return () => clearTimeout(timer)
    }
  }, [error, retryCount, maxRetries])

  return (
    <div
      ref={containerRef}
      className={cn("video-container group", className)}
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => setShowControls(false)}
    >
      <video
        ref={videoRef}
        className="w-full h-full object-contain"
        poster={poster}
        muted={isMuted}
        playsInline
      />

      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50">
          <div className="w-10 h-10 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      )}

      {/* Reconnecting overlay */}
      {isStalled && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 gap-3">
          <div className="w-10 h-10 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-yellow-500">Reconectando... ({stallRetryCount}/3)</p>
        </div>
      )}

      {/* Error overlay */}
      {(error || showStallError) && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 gap-3">
          <AlertCircle className="w-10 h-10 text-destructive" />
          <div className="text-center">
            <p className="text-sm text-muted-foreground">{error || 'Falha ao reconectar'}</p>
            {error?.includes('não está pronta') && retryCount < maxRetries && (
              <p className="text-xs text-muted-foreground mt-1">
                Tentativa {retryCount + 1}/{maxRetries + 1} em 3s...
              </p>
            )}
          </div>
          {(showStallError || (!error?.includes('não está pronta') || retryCount >= maxRetries)) && (
            <Button variant="secondary" size="sm" onClick={showStallError ? manualRetry : retry}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Tentar novamente
            </Button>
          )}
        </div>
      )}

      {/* Protocol indicator */}
      {!error && !isLoading && (
        <div className="absolute top-2 right-2 px-2 py-1 bg-black/60 rounded text-xs text-white">
          {protocol === 'webrtc' && '⚡ Baixa Latência'}
          {protocol === 'hls' && '📡 Modo Compatível'}
          {protocol === 'rtmp' && '📺 RTMP'}
        </div>
      )}

      {/* Controls overlay */}
      {!error && !isLoading && (
        <div
          className={cn(
            "absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 to-transparent transition-opacity",
            showControls ? "opacity-100" : "opacity-0"
          )}
        >
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-white hover:bg-white/20"
              onClick={togglePlay}
            >
              {isPlaying ? (
                <Pause className="w-4 h-4" />
              ) : (
                <Play className="w-4 h-4" />
              )}
            </Button>

            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-white hover:bg-white/20"
              onClick={toggleMute}
            >
              {isMuted ? (
                <VolumeX className="w-4 h-4" />
              ) : (
                <Volume2 className="w-4 h-4" />
              )}
            </Button>

            <div className="flex-1" />

            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-white hover:bg-white/20"
              onClick={toggleFullscreen}
            >
              <Maximize className="w-4 h-4" />
            </Button>

            {/* Recording Controls */}
            {showRecordingControls && (
              <>
                <Button
                  variant="ghost"
                  size="icon"
                  className={cn(
                    "h-8 w-8 hover:bg-white/20",
                    isRecording ? "text-red-500" : "text-white"
                  )}
                  onClick={toggleRecording}
                >
                  {isRecording ? (
                    <Square className="w-4 h-4" />
                  ) : (
                    <Circle className="w-4 h-4" />
                  )}
                </Button>

                {recordingStartTime && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-white hover:bg-white/20"
                    onClick={createClip}
                  >
                    <Scissors className="w-4 h-4" />
                  </Button>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
