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
  url: string
}

export function TimelinePlayerModal({ camera, onClose }: TimelinePlayerModalProps) {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [blocks, setBlocks] = useState<TimelineBlock[]>([])
  const [currentBlockIndex, setCurrentBlockIndex] = useState(0)
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
  const [bufferProgress, setBufferProgress] = useState(0)
  const hlsRef = useRef<Hls | null>(null)
  const pendingSeekRef = useRef<number | null>(null)

  // Iniciar cache ao abrir timeline
  useEffect(() => {
    axios.post(`http://localhost:8006/cache/start/${camera.id}`, null, {
      params: { date: selectedDate }
    }).catch(err => console.error('[Cache] Erro ao iniciar:', err))

    // Limpar cache ao fechar
    return () => {
      axios.post(`http://localhost:8006/cache/stop/${camera.id}`)
        .catch(err => console.error('[Cache] Erro ao parar:', err))
    }
  }, [camera.id, selectedDate])

  const togglePlay = () => {
    const video = videoRef.current
    if (!video) return
    
    if (isPlaying) {
      video.pause()
    } else {
      const playPromise = video.play()
      if (playPromise !== undefined) {
        playPromise.catch(() => {})
      }
    }
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
        console.log('[Timeline] Carregando:', camera.id, selectedDate)
        setBlocks([])
        
        const response = await recordingService.list({ camera_id: camera.id, date: selectedDate })
        
        if (response && response.recordings && Array.isArray(response.recordings)) {
          let filteredRecordings = response.recordings.filter((rec: any) => rec.camera_id === camera.id)
          
          if (timeFilter) {
            const [startH, startM] = timeFilter.start.split(':').map(Number)
            const [endH, endM] = timeFilter.end.split(':').map(Number)
            const filterStartMin = startH * 60 + startM
            const filterEndMin = endH * 60 + endM
            
            filteredRecordings = filteredRecordings.filter((rec: any) => {
              const [h, m] = rec.start_time.split(':').map(Number)
              const recMin = h * 60 + m
              return recMin >= filterStartMin && recMin <= filterEndMin
            })
          }
          
          const recordingBlocks: TimelineBlock[] = filteredRecordings.map((rec: any) => ({
            start_time: `${rec.date}T${rec.start_time}`,
            end_time: new Date(new Date(`${rec.date}T${rec.start_time}`).getTime() + (rec.duration_seconds * 1000)).toISOString(),
            url: rec.url || recordingService.getPlaybackUrl(rec.camera_id, rec.date, rec.filename)
          }))
          
          setBlocks(recordingBlocks)
          setCurrentTime(new Date())
        }
      } catch (error) {
        console.error('[Timeline] Erro:', error)
      }
    }
    loadRecordings()
  }, [camera.id, selectedDate, timeFilter])

  const timelineSegments = useMemo<TimelineSegment[]>(() => {
    return blocks.map(b => ({
      start: new Date(b.start_time),
      end: new Date(b.end_time),
      type: 'continuous'
    }))
  }, [blocks])

  const handleTimelineSeek = (seekDate: Date) => {
    // Se não tem filtro de hora, apenas navega no vídeo
    if (!timeFilter) {
      const seekTime = seekDate.getTime()
      
      const blockIndex = blocks.findIndex(b => {
        const start = new Date(b.start_time).getTime()
        const end = new Date(b.end_time).getTime()
        return seekTime >= start && seekTime <= end
      })

      if (blockIndex !== -1) {
        const block = blocks[blockIndex]
        const blockStart = new Date(block.start_time).getTime()
        const offsetSeconds = (seekTime - blockStart) / 1000

        if (blockIndex !== currentBlockIndex) {
          pendingSeekRef.current = offsetSeconds
          setCurrentBlockIndex(blockIndex)
        } else {
          if (videoRef.current) {
            videoRef.current.currentTime = offsetSeconds
          }
        }
        
        setCurrentTime(seekDate)
        setIsPlaying(true)
      }
      return
    }

    // Com filtro de hora ativo, permite seleção de clips
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

  const handleVideoLoadedMetadata = () => {
    if (videoRef.current && pendingSeekRef.current !== null) {
      videoRef.current.currentTime = pendingSeekRef.current
      pendingSeekRef.current = null
      if (isPlaying) {
          const playPromise = videoRef.current.play()
          if (playPromise !== undefined) {
            playPromise.catch(() => {
                setIsPlaying(false)
            })
          }
      }
    }
  }

  const handleTimeUpdate = () => {
    if (!videoRef.current || !blocks[currentBlockIndex]) return

    const block = blocks[currentBlockIndex]
    const blockStart = new Date(block.start_time).getTime()
    const videoCurrentTime = videoRef.current.currentTime * 1000

    const newTime = new Date(blockStart + videoCurrentTime)
    setCurrentTime(newTime)
  }

  const handleVideoEnd = () => {
    if (currentBlockIndex < blocks.length - 1) {
      setCurrentBlockIndex(prev => prev + 1)
      pendingSeekRef.current = 0
      setIsPlaying(true)
    } else {
      setIsPlaying(false)
    }
  }

  const handleCreateClip = async () => {
    if (!clipSelection.start || !clipSelection.end) return

    const durationMs = clipSelection.end.getTime() - clipSelection.start.getTime()
    const durationMinutes = durationMs / 1000 / 60

    if (durationMinutes > 10) {
      alert('O clip não pode ter mais de 10 minutos. Selecione um período menor.')
      return
    }

    if (durationMs < 1000) {
      alert('O clip deve ter pelo menos 1 segundo.')
      return
    }

    try {
      // Gerar nome do clip
      const clipName = `${camera.name} - ${clipSelection.start.toLocaleString('pt-BR')}`
      
      // Criar via API Django usando o serviço de API que já tem autenticação
      const { clipService } = await import('@/services/api')
      const clip = await clipService.create({
        camera_id: camera.id,
        name: clipName,
        start_time: clipSelection.start.toISOString(),
        end_time: clipSelection.end.toISOString(),
        quality: 'medium'
      })

      queryClient.invalidateQueries({ queryKey: ['clips'] })
      setClipSelection({ start: null, end: null })
      onClose()
      navigate('/clips')
    } catch (error) {
      console.error('Erro ao criar clip:', error)
      alert('Erro ao criar clip. Verifique se o serviço de clips está rodando.')
    }
  }

  const currentBlock = blocks[currentBlockIndex]

  useEffect(() => {
    const video = videoRef.current
    if (!video || !currentBlock) return

    setIsBuffering(true)
    const startTime = performance.now()
    console.log('[Player] Carregando:', currentBlock.url)

    if (hlsRef.current) {
      hlsRef.current.destroy()
      hlsRef.current = null
    }

    video.preload = 'metadata'
    video.src = currentBlock.url
    
    const handleLoadedMetadata = () => {
      const loadTime = performance.now() - startTime
      console.log(`[Player] Metadata carregado em ${loadTime.toFixed(0)}ms`)
      handleVideoLoadedMetadata()
    }

    const handleLoadedData = () => {
      const loadTime = performance.now() - startTime
      console.log(`[Player] Pronto para play em ${loadTime.toFixed(0)}ms`)
      setIsBuffering(false)
    }

    const handleWaiting = () => setIsBuffering(true)
    const handleCanPlay = () => setIsBuffering(false)

    video.addEventListener('loadedmetadata', handleLoadedMetadata)
    video.addEventListener('loadeddata', handleLoadedData)
    video.addEventListener('waiting', handleWaiting)
    video.addEventListener('canplay', handleCanPlay)

    return () => {
      video.removeEventListener('loadedmetadata', handleLoadedMetadata)
      video.removeEventListener('loadeddata', handleLoadedData)
      video.removeEventListener('waiting', handleWaiting)
      video.removeEventListener('canplay', handleCanPlay)
    }
  }, [currentBlockIndex, currentBlock])

  return (
    <div className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4">
      <button 
        onClick={onClose}
        className="fixed top-6 right-6 z-[60] p-3 bg-red-600 hover:bg-red-700 rounded-full transition-all text-white shadow-2xl"
        title="Fechar Timeline (Esc)"
      >
        <X className="w-6 h-6" />
      </button>
      
      <div className="w-full max-w-7xl h-[90vh] flex flex-col bg-black rounded-lg overflow-hidden shadow-2xl">
        <div className="h-[calc(100%-140px)] relative group">
          {currentBlock ? (
            <>
              <video
                ref={videoRef}
                key={currentBlockIndex}
                autoPlay={isPlaying}
                preload="metadata"
                playsInline
                className="w-full h-full object-contain"
                onTimeUpdate={handleTimeUpdate}
                onEnded={handleVideoEnd}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onWaiting={() => setIsBuffering(true)}
                onCanPlay={() => setIsBuffering(false)}
                controls={false}
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
              
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
              </div>
                
              <div className="absolute inset-0 flex items-center justify-center gap-4 pointer-events-none">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (currentBlockIndex > 0) {
                      setCurrentBlockIndex(currentBlockIndex - 1);
                      pendingSeekRef.current = 0;
                      setIsPlaying(true);
                    }
                  }}
                  disabled={currentBlockIndex === 0}
                  className="p-4 bg-black/50 hover:bg-black/70 rounded-full transition-all text-white disabled:opacity-30 disabled:cursor-not-allowed backdrop-blur-sm opacity-0 group-hover:opacity-100 pointer-events-auto"
                >
                  <SkipBack className="w-6 h-6" />
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    togglePlay();
                  }}
                  className="p-6 bg-white/90 hover:bg-white rounded-full transition-all text-black shadow-2xl opacity-0 group-hover:opacity-100 pointer-events-auto"
                >
                  {isPlaying ? <Pause className="w-8 h-8" /> : <Play className="w-8 h-8 ml-1" />}
                </button>
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (currentBlockIndex < blocks.length - 1) {
                      setCurrentBlockIndex(currentBlockIndex + 1);
                      pendingSeekRef.current = 0;
                      setIsPlaying(true);
                    }
                  }}
                  disabled={currentBlockIndex >= blocks.length - 1}
                  className="p-4 bg-black/50 hover:bg-black/70 rounded-full transition-all text-white disabled:opacity-30 disabled:cursor-not-allowed backdrop-blur-sm opacity-0 group-hover:opacity-100 pointer-events-auto"
                >
                  <SkipForward className="w-6 h-6" />
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
              <div className="text-gray-400 flex flex-col items-center gap-3">
                <div className="w-12 h-12 rounded-full border-2 border-gray-700 border-t-white animate-spin" />
                <p className="text-sm">Carregando gravação...</p>
              </div>
            </div>
          )}
        </div>

        <div className="h-[140px] bg-zinc-900 flex-shrink-0 border-t border-zinc-800">
          <div className="flex items-center gap-4 px-4 py-2 border-b border-zinc-800 relative z-10">
            <select
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="px-3 py-1.5 bg-zinc-800 text-white text-sm rounded border border-zinc-700 focus:outline-none focus:border-purple-500 relative z-20"
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
                className="px-2 py-1.5 bg-zinc-800 text-white text-sm rounded border border-zinc-700 focus:outline-none focus:border-purple-500 [color-scheme:dark]"
                placeholder="Início"
              />
              <span className="text-zinc-500">até</span>
              <input
                type="time"
                value={timeFilter?.end || ''}
                onChange={(e) => setTimeFilter(prev => ({ start: prev?.start || '00:00', end: e.target.value }))}
                className="px-2 py-1.5 bg-zinc-800 text-white text-sm rounded border border-zinc-700 focus:outline-none focus:border-purple-500 [color-scheme:dark]"
                placeholder="Fim"
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
            
            <div className="text-xs text-zinc-500 border-l border-zinc-700 pl-3">
              {timeFilter ? 'Clique na timeline para selecionar trecho do clip' : 'Clique na timeline para navegar no vídeo'}
            </div>
            
            <div className="ml-auto flex items-center gap-3">
              {clipSelection.start && clipSelection.end && (
                <div className="text-xs font-mono">
                  <span className={(
                    (clipSelection.end.getTime() - clipSelection.start.getTime()) / 1000 / 60 > 10
                      ? "text-red-400"
                      : "text-purple-400"
                  )}>
                    {clipSelection.start.toLocaleTimeString('pt-BR')} - {clipSelection.end.toLocaleTimeString('pt-BR')}
                    {' '}({Math.floor((clipSelection.end.getTime() - clipSelection.start.getTime()) / 1000 / 60)}min)
                  </span>
                </div>
              )}
              
              <div className="text-sm text-zinc-400">
                {blocks.length} gravações
              </div>
            </div>

            <button
              onClick={handleCreateClip}
              disabled={
                !timeFilter ||
                !clipSelection.start || 
                !clipSelection.end || 
                (clipSelection.end.getTime() - clipSelection.start.getTime()) / 1000 / 60 > 10
              }
              title={
                !timeFilter
                  ? "Ative o filtro de hora para criar clips"
                  : !clipSelection.start || !clipSelection.end 
                    ? "Clique na timeline para selecionar início e fim" 
                    : (clipSelection.end.getTime() - clipSelection.start.getTime()) / 1000 / 60 > 10
                      ? "Clip não pode ter mais de 10 minutos"
                      : "Criar clip do trecho selecionado"
              }
              className="px-3 py-1.5 rounded text-sm font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed bg-purple-600 text-white hover:bg-purple-700 disabled:hover:bg-purple-600"
            >
              <Scissors className="w-4 h-4" />
              Criar Clip
            </button>
          </div>
          
          <CanvasTimeline
            key={`timeline-${currentBlockIndex}-${selectedDate}`}
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
