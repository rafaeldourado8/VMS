import { useEffect, useRef, useState } from 'react'

interface PlayerState {
  volume: number
  quality: string
}

interface UseVideoPlayerOptions {
  onStalled?: () => void
  onRecovery?: () => void
  onError?: (error: string) => void
}

export function useVideoPlayer(videoRef: React.RefObject<HTMLVideoElement>, options: UseVideoPlayerOptions = {}) {
  const [isStalled, setIsStalled] = useState(false)
  const [retryCount, setRetryCount] = useState(0)
  const [showError, setShowError] = useState(false)
  const stallCheckInterval = useRef<NodeJS.Timeout | null>(null)
  const reloadTimestamps = useRef<number[]>([])
  const MAX_RETRIES = 3
  const RETRY_WINDOW = 60000 // 1 minute

  // Load player state from localStorage
  const loadPlayerState = (): PlayerState => {
    try {
      const saved = localStorage.getItem('vms_player_state')
      return saved ? JSON.parse(saved) : { volume: 1, quality: 'auto' }
    } catch {
      return { volume: 1, quality: 'auto' }
    }
  }

  // Save player state to localStorage
  const savePlayerState = (state: Partial<PlayerState>) => {
    try {
      const current = loadPlayerState()
      const updated = { ...current, ...state }
      localStorage.setItem('vms_player_state', JSON.stringify(updated))
    } catch (error) {
      console.error('Failed to save player state:', error)
    }
  }

  // Check if can retry (max 3x/min)
  const canRetry = (): boolean => {
    const now = Date.now()
    reloadTimestamps.current = reloadTimestamps.current.filter(t => now - t < RETRY_WINDOW)
    return reloadTimestamps.current.length < MAX_RETRIES
  }

  // Reload stream
  const reloadStream = () => {
    const video = videoRef.current
    if (!video) return

    if (!canRetry()) {
      setShowError(true)
      setIsStalled(false)
      options.onError?.('Limite de tentativas atingido')
      return
    }

    reloadTimestamps.current.push(Date.now())
    setRetryCount(prev => prev + 1)
    setIsStalled(true)
    options.onStalled?.()

    video.load()
    video.play().catch(() => {})

    setTimeout(() => {
      if (video.readyState >= 3) {
        setIsStalled(false)
        setRetryCount(0)
        options.onRecovery?.()
      }
    }, 3000)
  }

  // Check for stalled stream
  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    stallCheckInterval.current = setInterval(() => {
      if (video.readyState < 3 && !video.paused) {
        const stallDuration = 5000
        setTimeout(() => {
          if (video.readyState < 3 && !video.paused) {
            reloadStream()
          }
        }, stallDuration)
      }
    }, 5000)

    return () => {
      if (stallCheckInterval.current) clearInterval(stallCheckInterval.current)
    }
  }, [videoRef])

  // Apply saved state on mount
  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const state = loadPlayerState()
    video.volume = state.volume
  }, [videoRef])

  const setVolume = (volume: number) => {
    const video = videoRef.current
    if (video) {
      video.volume = volume
      savePlayerState({ volume })
    }
  }

  const setQuality = (quality: string) => {
    savePlayerState({ quality })
  }

  const manualRetry = () => {
    setShowError(false)
    setRetryCount(0)
    reloadTimestamps.current = []
    reloadStream()
  }

  return {
    isStalled,
    retryCount,
    showError,
    setVolume,
    setQuality,
    manualRetry,
    playerState: loadPlayerState(),
  }
}
