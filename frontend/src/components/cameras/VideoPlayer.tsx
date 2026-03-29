import { useEffect, useRef, useState } from 'react'
import Hls from 'hls.js'
import { Play, Pause, Volume2, VolumeX, Maximize, Minimize, RefreshCw, AlertCircle, Scissors, Circle, Square, Radio } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui'

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
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const hlsRef = useRef<Hls | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  
  const [isPlaying, setIsPlaying] = useState(autoPlay)
  const [isMuted, setIsMuted] = useState(muted)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showControls, setShowControls] = useState(false)
  const [retryCount, setRetryCount] = useState(0)
  const [isRecording, setIsRecording] = useState(false)
  const [recordingStartTime, setRecordingStartTime] = useState<Date | null>(null)
  const [showClipModal, setShowClipModal] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const maxRetries = 3

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const handleTimeUpdate = () => setCurrentTime(video.currentTime)
    const handleDurationChange = () => setDuration(video.duration)
    const handlePlay = () => setIsPlaying(true)
    const handlePause = () => setIsPlaying(false)

    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('durationchange', handleDurationChange)
    video.addEventListener('play', handlePlay)
    video.addEventListener('pause', handlePause)

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('durationchange', handleDurationChange)
      video.removeEventListener('play', handlePlay)
      video.removeEventListener('pause', handlePause)
    }
  }, [])

  useEffect(() => {
    const video = videoRef.current
    if (!video || !src) return

    setIsLoading(true)
    setError(null)

    // Verificar se é HLS
    if (src.includes('.m3u8')) {
      if (Hls.isSupported()) {
        const hls = new Hls({
          lowLatencyMode: false,
          backBufferLength: 5,
          maxBufferLength: 12,
          maxBufferSize: 15 * 1000 * 1000,
          maxMaxBufferLength: 20,
          liveSyncDurationCount: 3,
          liveMaxLatencyDurationCount: 5,
          manifestLoadingMaxRetry: 2,
          manifestLoadingRetryDelay: 2000,
          levelLoadingMaxRetry: 2,
          fragLoadingMaxRetry: 2,
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
          if (data.fatal) {
            console.log('HLS Fatal Error:', data)
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
          if (video) {
            video.pause()
            video.src = ''
            video.load()
          }
          hls.destroy()
          hlsRef.current = null
        }
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        // Safari nativo
        video.src = src
        video.addEventListener('loadedmetadata', () => {
          setIsLoading(false)
          if (autoPlay) video.play()
          onReady?.()
        })
        
        return () => {
          video.pause()
          video.src = ''
          video.load()
        }
      }
    } else {
      // HLS VOD (Timeline) - adiciona .m3u8 se necessário
      const vodUrl = src.includes('.m3u8') ? src : `${src}/index.m3u8`
      
      if (Hls.isSupported()) {
        const hls = new Hls({
          backBufferLength: 90,
          maxBufferLength: 180,
        })

        hls.loadSource(vodUrl)
        hls.attachMedia(video)

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          setIsLoading(false)
          if (autoPlay) {
            video.play().catch(() => {})
          }
          onReady?.()
        })

        hls.on(Hls.Events.ERROR, (_, data) => {
          if (data.fatal) {
            setError('Erro ao carregar gravação')
            setIsLoading(false)
            onError?.(data.details || 'VOD error')
          }
        })

        hlsRef.current = hls

        return () => {
          if (video) {
            video.pause()
            video.src = ''
            video.load()
          }
          hls.destroy()
          hlsRef.current = null
        }
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = vodUrl
        video.addEventListener('loadedmetadata', () => {
          setIsLoading(false)
          if (autoPlay) video.play()
          onReady?.()
        })
        
        return () => {
          video.pause()
          video.src = ''
          video.load()
        }
      }
    }

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

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const video = videoRef.current
    if (!video || !duration || src.includes('.m3u8')) return

    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const percentage = x / rect.width
    video.currentTime = percentage * duration
  }

  const formatTime = (seconds: number) => {
    if (!isFinite(seconds)) return '00:00'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
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

  // Reconecta stream a cada 45min para evitar memory leak
  useEffect(() => {
    if (!src.includes('.m3u8')) return // Só para live streams
    
    const reconnectInterval = setInterval(() => {
      if (hlsRef.current && !error) {
        const video = videoRef.current
        const wasPlaying = video && !video.paused
        
        hlsRef.current.destroy()
        
        const hls = new Hls({
          lowLatencyMode: false,
          backBufferLength: 5,
          maxBufferLength: 12,
          maxBufferSize: 15 * 1000 * 1000,
          maxMaxBufferLength: 20,
          liveSyncDurationCount: 3,
          liveMaxLatencyDurationCount: 5,
          manifestLoadingMaxRetry: 2,
          manifestLoadingRetryDelay: 2000,
          levelLoadingMaxRetry: 2,
          fragLoadingMaxRetry: 2,
        })
        
        hls.loadSource(src)
        if (video) hls.attachMedia(video)
        
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          if (wasPlaying && video) video.play()
        })
        
        hlsRef.current = hls
      }
    }, 45 * 60 * 1000)
    
    return () => clearInterval(reconnectInterval)
  }, [src, error])

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
      className={cn("relative", className)}
      onMouseEnter={() => setShowControls(true)}
      onMouseLeave={() => setShowControls(false)}
    >
      <video
        ref={videoRef}
        className="w-full h-full object-contain bg-black"
        poster={poster}
        muted={isMuted}
        playsInline
      />

      {/* LIVE badge */}
      {!error && !isLoading && src.includes('.m3u8') && isPlaying && (
        <div className="absolute top-3 left-3 z-10">
          <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-red-600/90 text-white text-xs font-semibold backdrop-blur-sm">
            <Radio className="w-3 h-3 animate-live-pulse" />
            AO VIVO
          </div>
        </div>
      )}

      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-3">
            <div className="w-10 h-10 border-2 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin" />
            <span className="text-xs text-white/60">Conectando...</span>
          </div>
        </div>
      )}

      {/* Error overlay */}
      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 backdrop-blur-sm gap-3">
          <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center">
            <AlertCircle className="w-6 h-6 text-red-400" />
          </div>
          <div className="text-center">
            <p className="text-sm text-white/70">{error}</p>
            {error.includes('não está pronta') && retryCount < maxRetries && (
              <p className="text-xs text-white/40 mt-1">
                Tentativa {retryCount + 1}/{maxRetries + 1} em 3s...
              </p>
            )}
          </div>
          {(!error.includes('não está pronta') || retryCount >= maxRetries) && (
            <Button variant="secondary" size="sm" onClick={retry} className="bg-white/10 hover:bg-white/20 text-white border-0">
              <RefreshCw className="w-4 h-4 mr-2" />
              Tentar novamente
            </Button>
          )}
        </div>
      )}

      {/* Controls overlay */}
      {!error && !isLoading && (
        <div
          className={cn(
            "player-controls absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent pt-10",
            showControls ? "opacity-100" : "opacity-0"
          )}
        >
          {/* Progress Bar */}
          {duration > 0 && !src.includes('.m3u8') && (
            <div
              className="px-3 pt-2 cursor-pointer group/progress"
              onClick={handleProgressClick}
            >
              <div className="h-1 group-hover/progress:h-1.5 bg-white/20 rounded-full overflow-hidden transition-all">
                <div
                  className="h-full bg-cyan-400 rounded-full transition-all"
                  style={{ width: `${(currentTime / duration) * 100}%` }}
                />
              </div>
              <div className="flex justify-between text-[10px] text-white/50 mt-1 font-mono">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>
          )}

          <div className="flex items-center gap-1 px-2 pb-2">
            <button
              className="h-8 w-8 flex items-center justify-center rounded-md text-white/80 hover:text-white hover:bg-white/10 transition-colors"
              onClick={togglePlay}
            >
              {isPlaying ? (
                <Pause className="w-4 h-4" fill="currentColor" />
              ) : (
                <Play className="w-4 h-4" fill="currentColor" />
              )}
            </button>

            <button
              className="h-8 w-8 flex items-center justify-center rounded-md text-white/80 hover:text-white hover:bg-white/10 transition-colors"
              onClick={toggleMute}
            >
              {isMuted ? (
                <VolumeX className="w-4 h-4" />
              ) : (
                <Volume2 className="w-4 h-4" />
              )}
            </button>

            <div className="flex-1" />

            {/* Recording Controls */}
            {showRecordingControls && (
              <>
                <button
                  className={cn(
                    "h-8 w-8 flex items-center justify-center rounded-md hover:bg-white/10 transition-colors",
                    isRecording ? "text-red-400" : "text-white/80 hover:text-white"
                  )}
                  onClick={toggleRecording}
                >
                  {isRecording ? (
                    <Square className="w-3.5 h-3.5" fill="currentColor" />
                  ) : (
                    <Circle className="w-4 h-4" />
                  )}
                </button>

                {recordingStartTime && (
                  <button
                    className="h-8 w-8 flex items-center justify-center rounded-md text-white/80 hover:text-white hover:bg-white/10 transition-colors"
                    onClick={createClip}
                  >
                    <Scissors className="w-4 h-4" />
                  </button>
                )}
              </>
            )}

            <button
              className="h-8 w-8 flex items-center justify-center rounded-md text-white/80 hover:text-white hover:bg-white/10 transition-colors"
              onClick={toggleFullscreen}
            >
              {document.fullscreenElement ? (
                <Minimize className="w-4 h-4" />
              ) : (
                <Maximize className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
