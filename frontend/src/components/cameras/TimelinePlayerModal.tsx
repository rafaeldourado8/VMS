import { useState, useRef, useMemo, useEffect } from 'react'
import { Camera } from '@/types'
import { X, Play, Pause, SkipBack, SkipForward, Scissors } from 'lucide-react'
import { CanvasTimeline, TimelineSegment } from './CanvasTimeline'
import { recordingService } from '@/services/api'
import { useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import Hls from 'hls.js'
import axios from 'axios'

interface TimelinePlayerModalProps {
  camera: Camera
  onClose: () => void
}

interface TimelineBlock {
  start_time: string
  end_time: string
  duration_seconds: number
}

export function TimelinePlayerModal({ camera, onClose }: TimelinePlayerModalProps) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [blocks, setBlocks] = useState<TimelineBlock[]>([])
  const [isPlaying, setIsPlaying] = useState(true)
  const [currentTime, setCurrentTime] = useState<Date>(new Date())
  
  const today = new Date()
  const localDate = new Date(today.getTime() - (today.getTimezoneOffset() * 60000))
  const [selectedDate, setSelectedDate] = useState<string>(localDate.toISOString().split('T')[0])
  const [availableDates, setAvailableDates] = useState<string[]>([])
  const [timeFilter, setTimeFilter] = useState<{ start: string; end: string } | null>(null)
  const [clipSelection, setClipSelection] = useState<{ start: Date | null; end: Date | null }>({ start: null, end: null })
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isBuffering, setIsBuffering] = useState(false)
  const hlsRef = useRef<Hls | null>(null)
  
  // URL da Playlist Mestre do Dia (via HAProxy)
  const masterPlaylistUrl = `/vod/playlist/${camera.id}/${selectedDate}/index.m3u8`

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
        const { data } = await axios.get(`http://localhost:8003/recordings/available-dates/${camera.id}`)
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
        const response = await recordingService.list({ camera_id: camera.id, date: selectedDate })
        
        if (response && response.recordings && Array.isArray(response.recordings)) {
          let filteredRecordings = response.recordings.filter((rec: any) => rec.camera_id === camera.id)
          
          const recordingBlocks: TimelineBlock[] = filteredRecordings.map((rec: any) => ({
            start_time: `${rec.date}T${rec.start_time}`,
            end_time: new Date(new Date(`${rec.date}T${rec.start_time}`).getTime() + (rec.duration_seconds * 1000)).toISOString(),
            duration_seconds: rec.duration_seconds
          }))
          
          // Ordenar para garantir que o cálculo de tempo funcione
          recordingBlocks.sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
          
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

  // --- LÓGICA DE MAPEAMENTO DE TEMPO ---
  
  // Converte Hora Real (ex: 11:30:00) para Segundos do Vídeo
  const wallClockToVideoTime = (targetDate: Date): number => {
    let accumulatedSeconds = 0
    const targetTime = targetDate.getTime()

    for (const block of blocks) {
      const start = new Date(block.start_time).getTime()
      const end = new Date(block.end_time).getTime()

      if (targetTime >= start && targetTime <= end) {
        return accumulatedSeconds + ((targetTime - start) / 1000)
      } else if (targetTime > end) {
        accumulatedSeconds += block.duration_seconds
      } else if (targetTime < start) {
        return accumulatedSeconds // Caiu em um buraco, pula pro início do próximo
      }
    }
    return accumulatedSeconds
  }

  // Converte Segundos do Vídeo para Hora Real
  const videoTimeToWallClock = (videoSeconds: number): Date => {
    let remaining = videoSeconds
    for (const block of blocks) {
      if (remaining <= block.duration_seconds) {
        return new Date(new Date(block.start_time).getTime() + (remaining * 1000))
      }
      remaining -= block.duration_seconds
    }
    return blocks.length > 0 ? new Date(blocks[blocks.length - 1].end_time) : new Date()
  }

  // -------------------------------------

  const handleTimelineSeek = (seekDate: Date) => {
    if (!timeFilter) {
      if (videoRef.current && blocks.length > 0) {
        const videoTime = wallClockToVideoTime(seekDate)
        videoRef.current.currentTime = videoTime
        setCurrentTime(seekDate)
        setIsPlaying(true)
        videoRef.current.play().catch(() => {})
      }
      return
    }

    if (!clipSelection.start) {
      setClipSelection({ start: seekDate, end: null })
      return
    }
    if (!clipSelection.end) {
      if (seekDate > clipSelection.start) {
        setClipSelection(prev => ({ ...prev, end: seekDate }))
      } else {
        setClipSelection({ start: seekDate, end: null })
      }
      return
    }
    setClipSelection({ start: seekDate, end: null })
  }

  const handleTimeUpdate = () => {
    if (!videoRef.current || blocks.length === 0) return
    const newTime = videoTimeToWallClock(videoRef.current.currentTime)
    setCurrentTime(newTime)
  }

  const handleCreateClip = async () => {
    if (!clipSelection.start || !clipSelection.end) return
    const durationMs = clipSelection.end.getTime() - clipSelection.start.getTime()
    if (durationMs / 1000 / 60 > 10) return alert('Máximo 10 minutos.')
    if (durationMs < 1000) return alert('Mínimo 1 segundo.')

    try {
      const clipName = `${camera.name} - ${clipSelection.start.toLocaleString('pt-BR')}`
      const { clipService } = await import('@/services/api')
      await clipService.create({
        camera_id: camera.id,
        name: clipName,
        start_time: clipSelection.start.toISOString(),
        end_time: clipSelection.end.toISOString(),
        quality: 'medium'
      })
      queryClient.invalidateQueries({ queryKey: ['clips'] })
      onClose()
      navigate('/clips')
    } catch (error) {
      console.error('Erro ao criar clip:', error)
    }
  }

  // INICIALIZAR PLAYER HLS.js
  useEffect(() => {
    const video = videoRef.current
    if (!video || blocks.length === 0) return

    setIsBuffering(true)

    if (hlsRef.current) {
      hlsRef.current.destroy()
    }

    if (Hls.isSupported()) {
      const hls = new Hls({
        backBufferLength: 90,
        maxBufferLength: 180,
      })

      hls.loadSource(masterPlaylistUrl)
      hls.attachMedia(video)

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        setIsBuffering(false)
        if (isPlaying) video.play().catch(() => {})
      })

      hls.on(Hls.Events.ERROR, (_, data) => {
        if (data.fatal) setIsBuffering(false)
      })

      hlsRef.current = hls

      return () => hls.destroy()
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = masterPlaylistUrl
      video.addEventListener('loadedmetadata', () => setIsBuffering(false))
    }
  }, [masterPlaylistUrl, blocks.length]) // Recarrega se a data/câmera mudar

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
                className="w-full h-full object-contain"
                onTimeUpdate={handleTimeUpdate}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onWaiting={() => setIsBuffering(true)}
                onCanPlay={() => setIsBuffering(false)}
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
                <button
                  onClick={(e) => { e.stopPropagation(); togglePlay(); }}
                  className="p-6 bg-white/90 hover:bg-white rounded-full transition-all text-black shadow-2xl opacity-0 group-hover:opacity-100 pointer-events-auto"
                >
                  {isPlaying ? <Pause className="w-8 h-8" /> : <Play className="w-8 h-8 ml-1" />}
                </button>
              </div>
              
              {isBuffering && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                  <div className="w-16 h-16 rounded-full border-4 border-gray-700 border-t-white animate-spin" />
                </div>
              )}
            </>
          ) : (
            <div className="absolute inset-0 flex items-center justify-center bg-black">
              <div className="text-gray-400">Nenhuma gravação para esta data.</div>
            </div>
          )}
        </div>

        {/* ... (O resto do footer, os filtros e a CanvasTimeline se mantêm idênticos) ... */}
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
          />
        </div>
      </div>
    </div>
  )
}