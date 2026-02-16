import { useState, useRef, useMemo, useEffect } from 'react'
import { Camera } from '@/types'
import { X, Play, Pause, SkipBack, SkipForward } from 'lucide-react'
import { CanvasTimeline, TimelineSegment } from './CanvasTimeline'
import { recordingService } from '@/services/api'

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
  // Dados das gravações
  const [blocks, setBlocks] = useState<TimelineBlock[]>([])
  
  // Estado do Player
  const [currentBlockIndex, setCurrentBlockIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState<Date>(new Date())
  
  // Refs para controle fino de seek e sincronização
  const videoRef = useRef<HTMLVideoElement>(null)
  const pendingSeekRef = useRef<number | null>(null)

  useEffect(() => {
    const loadRecordings = async () => {
      try {
        // Usar data atual correta
        const today = new Date()
        const yesterday = new Date(today)
        yesterday.setDate(yesterday.getDate() - 1)
        
        const dates = [
          today.toISOString().split('T')[0],
          yesterday.toISOString().split('T')[0]
        ]
        
        console.log('[Timeline] Buscando gravações para datas:', dates)
        
        let allRecordings: any[] = []
        
        for (const date of dates) {
          try {
            console.log('[Timeline] Tentando data:', date)
            const response = await recordingService.list({ camera_id: camera.id, date })
            
            console.log('[Timeline] API Response para', date, ':', response)
            
            if (response && response.recordings && Array.isArray(response.recordings)) {
              allRecordings = [...allRecordings, ...response.recordings]
            }
          } catch (err: any) {
            if (err.response?.status === 401) {
              console.error('[Timeline] Erro 401: Faça login novamente')
              return
            }
            console.error('[Timeline] Erro ao buscar', date, ':', err)
          }
        }
        
        console.log('[Timeline] Total de gravações encontradas:', allRecordings.length)
        
        if (allRecordings.length === 0) {
          console.log('[Timeline] Nenhuma gravação encontrada')
          return
        }
        
        const recordingBlocks: TimelineBlock[] = allRecordings.map((rec: any) => {
          const startTime = `${rec.date}T${rec.start_time}`
          const endTime = new Date(new Date(startTime).getTime() + (rec.duration_seconds * 1000)).toISOString()
          const videoUrl = rec.url || recordingService.getPlaybackUrl(rec.camera_id, rec.date, rec.filename)
          
          console.log('[Timeline] Bloco:', { startTime, endTime, videoUrl })
          
          return {
            start_time: startTime,
            end_time: endTime,
            url: videoUrl
          }
        })
        
        console.log('[Timeline] Total de blocos:', recordingBlocks.length)
        setBlocks(recordingBlocks)
        
        if (recordingBlocks.length > 0) {
          setCurrentTime(new Date(recordingBlocks[0].start_time))
        }
      } catch (error) {
        console.error('[Timeline] Erro ao carregar gravações:', error)
      }
    }
    loadRecordings()
  }, [camera.id])

  // Transforma blocos em segmentos para o Canvas (Memoizado para alta performance)
  const timelineSegments = useMemo<TimelineSegment[]>(() => {
    return blocks.map(b => ({
      start: new Date(b.start_time),
      end: new Date(b.end_time),
      type: 'continuous' // Futuramente, se a API suportar, pode detectar 'motion'
    }))
  }, [blocks])

  // --- LÓGICA DE SINCRONIA: TIMELINE -> VIDEO ---
  
  const handleTimelineSeek = (seekDate: Date) => {
    const seekTime = seekDate.getTime()
    
    // 1. Acha qual bloco contém esse tempo
    const blockIndex = blocks.findIndex(b => {
      const start = new Date(b.start_time).getTime()
      const end = new Date(b.end_time).getTime()
      return seekTime >= start && seekTime <= end
    })

    if (blockIndex !== -1) {
      // Estamos dentro de um bloco existente (Gravação)
      const block = blocks[blockIndex]
      const blockStart = new Date(block.start_time).getTime()
      const offsetSeconds = (seekTime - blockStart) / 1000

      // Se mudou de bloco (arquivo), precisamos carregar o novo video
      if (blockIndex !== currentBlockIndex) {
        pendingSeekRef.current = offsetSeconds // Guarda o seek para aplicar após o load
        setCurrentBlockIndex(blockIndex)
      } else {
        // Mesmo bloco, seek imediato
        if (videoRef.current) {
          videoRef.current.currentTime = offsetSeconds
        }
      }
      
      setCurrentTime(seekDate)
      setIsPlaying(true)
    } else {
      // Clicou num buraco (gap) - Apenas move a agulha visualmente
      setCurrentTime(seekDate)
      // Opcional: Pausar o vídeo pois não há gravação aqui
      // setIsPlaying(false) 
    }
  }

  // Quando o video carrega os metadados (ex: após troca de bloco), aplica o seek pendente
  const handleVideoLoadedMetadata = () => {
    if (videoRef.current && pendingSeekRef.current !== null) {
      videoRef.current.currentTime = pendingSeekRef.current
      pendingSeekRef.current = null
      if (isPlaying) {
          const playPromise = videoRef.current.play()
          if (playPromise !== undefined) {
            playPromise.catch(() => {
                // Auto-play foi impedido pelo navegador
                setIsPlaying(false)
            })
          }
      }
    }
  }

  // --- LÓGICA DE SINCRONIA: VIDEO -> TIMELINE ---

  const handleTimeUpdate = () => {
    if (!videoRef.current || !blocks[currentBlockIndex]) return

    const currentBlock = blocks[currentBlockIndex]
    const blockStart = new Date(currentBlock.start_time).getTime()
    const videoCurrentTime = videoRef.current.currentTime * 1000 // ms

    // Atualiza a agulha global da timeline
    setCurrentTime(new Date(blockStart + videoCurrentTime))
  }

  const handleVideoEnd = () => {
    if (currentBlockIndex < blocks.length - 1) {
      // Pula para o próximo bloco automaticamente (reprodução contínua)
      setCurrentBlockIndex(prev => prev + 1)
      pendingSeekRef.current = 0 // Começa do zero no próximo
      setIsPlaying(true)
    } else {
      setIsPlaying(false)
    }
  }

  // Controles Simples
  const togglePlay = () => {
    const video = videoRef.current
    if (!video) return
    
    if (isPlaying) {
      video.pause()
      setIsPlaying(false)
    } else {
      video.play()
      setIsPlaying(true)
    }
  }

  const jumpEvent = (direction: 'prev' | 'next') => {
    if (direction === 'prev' && currentBlockIndex > 0) {
      setCurrentBlockIndex(currentBlockIndex - 1)
      pendingSeekRef.current = 0
    } else if (direction === 'next' && currentBlockIndex < blocks.length - 1) {
      setCurrentBlockIndex(currentBlockIndex + 1)
      pendingSeekRef.current = 0
    }
    setIsPlaying(true)
  }


  // --- RENDER ---
  
  const currentBlock = blocks[currentBlockIndex]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black">
      <div className="w-full h-full flex flex-col">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-3 bg-gray-950/80 backdrop-blur absolute top-0 w-full z-10 border-b border-white/10">
          <div>
            <h2 className="text-lg font-bold text-white leading-tight">{camera.name}</h2>
            <p className="text-xs text-blue-400 font-mono">
              {currentTime.toLocaleDateString('pt-BR')} {currentTime.toLocaleTimeString('pt-BR')}
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-red-500/20 hover:text-red-500 rounded-full transition-colors text-gray-400">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Video Area (Ocupa o máximo possível) */}
        <div className="flex-1 bg-black flex items-center justify-center overflow-hidden pt-16 pb-[140px]">
          {currentBlock ? (
            <video
              ref={videoRef}
              key={currentBlock.url} // Força reload completo do elemento se mudar URL (limpa buffers)
              src={currentBlock.url}
              autoPlay={isPlaying}
              className="max-w-full max-h-full shadow-2xl"
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleVideoLoadedMetadata}
              onEnded={handleVideoEnd}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              // Desabilita controles nativos para usar os nossos
              controls={false} 
            />
          ) : (
            <div className="text-gray-500 flex flex-col items-center gap-2">
              <div className="w-12 h-12 rounded-full border-2 border-gray-700 border-t-blue-500 animate-spin" />
              <p>Carregando gravação...</p>
            </div>
          )}
        </div>

        {/* Bottom Panel: Controls + Canvas Timeline */}
        <div className="h-[140px] bg-gray-950 border-t border-gray-800 flex flex-col absolute bottom-0 w-full z-20">
          
          {/* Controles Player */}
          <div className="flex items-center justify-center gap-4 py-2 border-b border-gray-900 bg-gray-900/50">
            <button 
                onClick={() => jumpEvent('prev')} 
                disabled={currentBlockIndex === 0}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-full disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <SkipBack className="w-5 h-5" />
            </button>
            
            <button 
              onClick={togglePlay} 
              className="p-3 bg-white text-black hover:bg-blue-400 hover:text-white rounded-full transition-colors transform hover:scale-105 active:scale-95"
            >
              {isPlaying ? <Pause className="w-6 h-6 fill-current" /> : <Play className="w-6 h-6 fill-current" />}
            </button>
            
            <button 
                onClick={() => jumpEvent('next')} 
                disabled={currentBlockIndex >= blocks.length - 1}
                className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-full disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <SkipForward className="w-5 h-5" />
            </button>
          </div>

          {/* Canvas Timeline */}
          <div className="flex-1 relative">
            <CanvasTimeline
              segments={timelineSegments}
              currentTime={currentTime}
              onSeek={handleTimelineSeek}
              height={85}
            />
          </div>
        </div>

      </div>
    </div>
  )
}