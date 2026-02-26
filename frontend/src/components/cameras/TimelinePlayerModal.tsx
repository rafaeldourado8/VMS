import { useState, useRef, useMemo, useEffect } from 'react'
import { Camera } from '@/types'
import { X, Play, Pause, Scissors } from 'lucide-react'
import { CanvasTimeline, TimelineSegment } from './CanvasTimeline'
import { recordingService } from '@/services/api'
import { useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import api from '@/services/api'
import { getAuthenticatedVideoUrl } from '@/utils/videoAuth'

interface TimelinePlayerModalProps {
  camera: Camera
  onClose: () => void
}

interface TimelineBlock {
  start_time: string
  end_time: string
  duration_seconds: number
  file_path: string
}

export function TimelinePlayerModal({ camera, onClose }: TimelinePlayerModalProps) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [blocks, setBlocks] = useState<TimelineBlock[]>([])
  const [isPlaying, setIsPlaying] = useState(true)
  const [currentTime, setCurrentTime] = useState<Date>(new Date())
  const [currentBlockIndex, setCurrentBlockIndex] = useState(0)
  
  const today = new Date()
  const localDate = new Date(today.getTime() - (today.getTimezoneOffset() * 60000))
  const [selectedDate, setSelectedDate] = useState<string>(localDate.toISOString().split('T')[0])
  const [availableDates, setAvailableDates] = useState<string[]>([])
  const [timeFilter, setTimeFilter] = useState<{ start: string; end: string } | null>(null)
  const [clipSelection, setClipSelection] = useState<{ start: Date | null; end: Date | null }>({ start: null, end: null })
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isBuffering, setIsBuffering] = useState(false)

  const currentBlock = blocks[currentBlockIndex]
  const currentVideoUrl = currentBlock?.file_path || null

  const togglePlay = () => {
    const video = videoRef.current
    if (!video) return
    if (isPlaying) video.pause()
    else video.play().catch(() => {})
  }

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.code === 'Space') {
        e.preventDefault()
        togglePlay()
      } else if (e.code === 'Escape') {
        onClose()
      }
    }
    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [isPlaying])

  useEffect(() => {
    const loadAvailableDates = async () => {
      try {
        const storageUrl = import.meta.env.VITE_STORAGE_URL || '/storage'
        const { data } = await axios.get(`${storageUrl}/recordings/available-dates/${camera.id}`)
        setAvailableDates(data.dates || [])
      } catch (error) {
        console.error('[Timeline] Erro ao carregar datas:', error)
      }
    }
    loadAvailableDates()
  }, [camera.id])

  useEffect(() => {
    const loadRecordings = async () => {
      try {
        setBlocks([])
        setCurrentBlockIndex(0)
        
        const storageUrl = import.meta.env.VITE_STORAGE_URL || '/storage'
        const { data } = await axios.get(`${storageUrl}/timeline/${camera.id}`, {
          params: { date: selectedDate, limit: 100 }
        })
        
        if (data && data.blocks && Array.isArray(data.blocks)) {
          const recordingBlocks: TimelineBlock[] = data.blocks.map((block: any) => ({
            start_time: block.start_time,
            end_time: block.end_time,
            duration_seconds: block.duration_seconds,
            file_path: block.file_path
          }))
          
          setBlocks(recordingBlocks)
          if (recordingBlocks.length > 0) {
            setCurrentTime(new Date(recordingBlocks[0].start_time))
          }
        }
      } catch (error) {
        console.error('[Timeline] Erro:', error)
      }
    }
    loadRecordings()
  }, [camera.id, selectedDate])

  const timelineSegments = useMemo<TimelineSegment[]>(() => {
    return blocks.map(b => ({
      start: new Date(b.start_time),
      end: new Date(b.end_time),
      type: 'continuous'
    }))
  }, [blocks])

  const handleTimelineSeek = (seekDate: Date) => {
    const blockIndex = blocks.findIndex(b => {
      const start = new Date(b.start_time)
      const end = new Date(b.end_time)
      return seekDate >= start && seekDate <= end
    })

    if (blockIndex !== -1) {
      setCurrentBlockIndex(blockIndex)
      setCurrentTime(seekDate)
      
      if (videoRef.current) {
        const blockStart = new Date(blocks[blockIndex].start_time)
        const offsetSeconds = (seekDate.getTime() - blockStart.getTime()) / 1000
        videoRef.current.currentTime = offsetSeconds
      }
    }

    if (timeFilter) {
      if (!clipSelection.start) {
        setClipSelection({ start: seekDate, end: null })
      } else if (!clipSelection.end) {
        if (seekDate > clipSelection.start) {
          setClipSelection(prev => ({ ...prev, end: seekDate }))
        } else {
          setClipSelection({ start: seekDate, end: null })
        }
      } else {
        setClipSelection({ start: seekDate, end: null })
      }
      return
    }
    setClipSelection({ start: seekDate, end: null })
  }

  const handleTimeUpdate = () => {
    if (!videoRef.current || !currentBlock) return
    const video = videoRef.current
    const blockStart = new Date(currentBlock.start_time)
    const newTime = new Date(blockStart.getTime() + video.currentTime * 1000)
    setCurrentTime(newTime)
    
    // Auto-skip se estiver perto do fim e houver próximo bloco
    if (currentBlockIndex < blocks.length - 1) {
      const timeRemaining = video.duration - video.currentTime
      if (timeRemaining < 0.5 && timeRemaining > 0) {
        setCurrentBlockIndex(currentBlockIndex + 1)
      }
    }
  }

  const handleVideoEnded = () => {
    if (currentBlockIndex < blocks.length - 1) {
      setCurrentBlockIndex(currentBlockIndex + 1)
    } else {
      setIsPlaying(false)
    }
  }

  const handleCreateClip = async () => {
    if (!clipSelection.start || !clipSelection.end) return
    const durationMs = clipSelection.end.getTime() - clipSelection.start.getTime()
    if (durationMs / 1000 / 60 > 10) return alert('Máximo 10 minutos.')
    if (durationMs < 1000) return alert('Mínimo 1 segundo.')

    try {
      // Formatar sem timezone
      const formatLocal = (date: Date) => {
        const y = date.getFullYear()
        const m = String(date.getMonth() + 1).padStart(2, '0')
        const d = String(date.getDate()).padStart(2, '0')
        const h = String(date.getHours()).padStart(2, '0')
        const min = String(date.getMinutes()).padStart(2, '0')
        const s = String(date.getSeconds()).padStart(2, '0')
        return `${y}-${m}-${d}T${h}:${min}:${s}`
      }
      
      await axios.post('/api/clips-service/create', {
        camera_id: camera.id,
        start_time: formatLocal(clipSelection.start),
        end_time: formatLocal(clipSelection.end)
      })
      
      queryClient.invalidateQueries({ queryKey: ['clips'] })
      navigate('/clips')
    } catch (error) {
      console.error('Erro ao criar clip:', error)
      alert('Erro ao criar clip')
    }
  }

  const [videoBlob, setVideoBlob] = useState<string | null>(null)

  useEffect(() => {
    const video = videoRef.current
    if (!video || !currentVideoUrl) return

    console.log('[Video] Carregando:', currentVideoUrl)
    setIsBuffering(true)
    
    // Fetch com autenticação JWT
    const loadVideo = async () => {
      try {
        const token = localStorage.getItem('accessToken')
        const response = await fetch(currentVideoUrl, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        
        const blob = await response.blob()
        const blobUrl = URL.createObjectURL(blob)
        
        // Limpar blob anterior
        if (videoBlob) {
          URL.revokeObjectURL(videoBlob)
        }
        
        setVideoBlob(blobUrl)
        video.src = blobUrl
        video.load()
      } catch (error) {
        console.error('[Video] Erro ao carregar:', error)
        setIsBuffering(false)
      }
    }
    
    loadVideo()

    const handleCanPlay = () => {
      console.log('[Video] Pronto para reproduzir')
      setIsBuffering(false)
      if (isPlaying) video.play().catch(() => {})
    }

    const handleError = (e: Event) => {
      console.error('[Video] Erro ao carregar:', video.error)
      console.error('[Video] URL:', currentVideoUrl)
      console.error('[Video] Network State:', video.networkState)
      console.error('[Video] Ready State:', video.readyState)
      setIsBuffering(false)
    }

    video.addEventListener('canplay', handleCanPlay)
    video.addEventListener('error', handleError)
    
    return () => {
      video.removeEventListener('canplay', handleCanPlay)
      video.removeEventListener('error', handleError)
      if (videoBlob) {
        URL.revokeObjectURL(videoBlob)
      }
    }
  }, [currentVideoUrl, isPlaying])

  return (
    <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4">
      <button 
        onClick={onClose}
        className="fixed top-6 right-6 z-[60] p-3 bg-red-600 hover:bg-red-700 rounded-full transition-all text-white shadow-2xl"
      >
        <X className="w-6 h-6" />
      </button>
      
      <div className="w-full max-w-7xl h-[90vh] flex flex-col bg-black rounded-lg overflow-hidden shadow-2xl">
        <div className="h-[calc(100%-140px)] relative group">
          {blocks.length > 0 ? (
            <>
              <video
                ref={videoRef}
                autoPlay={isPlaying}
                playsInline
                preload="metadata"
                className="w-full h-full object-contain"
                onTimeUpdate={handleTimeUpdate}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onEnded={handleVideoEnded}
                onClick={togglePlay}
              />
              
              <div className="absolute top-0 left-0 right-0 flex items-center justify-between px-6 py-4 pointer-events-none">
                <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <h2 className="text-lg font-medium text-white drop-shadow-lg">{camera.name}</h2>
                  <p className="text-sm text-gray-300 font-mono mt-1">
                    {currentTime.toLocaleDateString('pt-BR')} {currentTime.toLocaleTimeString('pt-BR')}
                  </p>
                </div>
              </div>
                
              <div className="absolute inset-0 flex items-center justify-center gap-4 pointer-events-none">
                {!isBuffering && (
                  <button
                    onClick={(e) => { e.stopPropagation(); togglePlay(); }}
                    className="p-6 bg-white/90 hover:bg-white rounded-full transition-all text-black shadow-2xl opacity-0 group-hover:opacity-100 pointer-events-auto"
                  >
                    {isPlaying ? <Pause className="w-8 h-8" /> : <Play className="w-8 h-8 ml-1" />}
                  </button>
                )}
              </div>
              
              {isBuffering && (
                <div className="absolute inset-0 bg-zinc-900 flex items-center justify-center">
                  <div className="w-20 h-20 rounded-full border-4 border-zinc-700 border-t-zinc-400 animate-spin" />
                </div>
              )}
            </>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center bg-black">
              <div className="text-gray-400">Nenhuma gravação para esta data.</div>
            </div>
          )}
        </div>

        <div className="h-[140px] bg-zinc-900 flex-shrink-0 border-t border-zinc-800">
          <div className="flex items-center gap-4 px-4 py-2 border-b border-zinc-800 relative z-10">
            <select
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="px-3 py-1.5 bg-zinc-800 text-white text-sm rounded border border-zinc-700 focus:outline-none focus:border-purple-500"
            >
              {availableDates.map(date => (
                <option key={date} value={date}>
                  {new Date(date + 'T00:00:00').toLocaleDateString('pt-BR')}
                </option>
              ))}
            </select>
            
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-500">Filtrar:</span>
              <input
                type="time"
                value={timeFilter?.start || ''}
                onChange={(e) => setTimeFilter(prev => ({ start: e.target.value, end: prev?.end || '23:59' }))}
                className="px-2 py-1.5 bg-zinc-800 text-white text-sm rounded border border-zinc-700"
              />
              <span className="text-zinc-500">até</span>
              <input
                type="time"
                value={timeFilter?.end || ''}
                onChange={(e) => setTimeFilter(prev => ({ start: prev?.start || '00:00', end: e.target.value }))}
                className="px-2 py-1.5 bg-zinc-800 text-white text-sm rounded border border-zinc-700"
              />
              {timeFilter && (
                <button
                  onClick={() => setTimeFilter(null)}
                  className="px-2 py-1 bg-zinc-700 hover:bg-zinc-600 text-white text-sm rounded"
                >
                  Limpar
                </button>
              )}
            </div>
            
            <button
              onClick={handleCreateClip}
              disabled={!timeFilter || !clipSelection.start || !clipSelection.end}
              className="ml-auto px-3 py-1.5 rounded text-sm font-medium bg-purple-600 text-white hover:bg-purple-700 disabled:opacity-50"
            >
              <Scissors className="w-4 h-4 inline-block mr-2" />
              Criar Clip
            </button>
          </div>
          
          <CanvasTimeline
            key={`timeline-${selectedDate}`}
            segments={timelineSegments}
            currentTime={currentTime}
            onSeek={handleTimelineSeek}
            height={60}
            clipSelection={timeFilter ? clipSelection : undefined}
            timeFilter={timeFilter}
          />
        </div>
      </div>
    </div>
  )
}
