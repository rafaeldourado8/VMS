import { useState, useRef, useEffect } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface TimelineBlock {
  start_time: string
  end_time: string
  file_path: string
  duration_seconds: number
  file_size_bytes: number
}

interface TimelineGap {
  start: string
  end: string
  duration_seconds: number
}

interface TimelineBarProps {
  blocks: TimelineBlock[]
  gaps?: TimelineGap[]
  currentTime: Date
  onTimeClick: (time: Date) => void
  timezone: string
}

export function TimelineBar({ blocks, gaps = [], currentTime, onTimeClick, timezone }: TimelineBarProps) {
  const timelineRef = useRef<HTMLDivElement>(null)

  if (blocks.length === 0) {
    return (
      <div className="text-center text-gray-500 py-4">
        Nenhuma gravação disponível (aguarde 2 minutos)
      </div>
    )
  }

  const firstBlock = new Date(blocks[0].start_time)
  const lastBlock = new Date(blocks[blocks.length - 1].end_time)
  const totalDuration = (lastBlock.getTime() - firstBlock.getTime()) / 1000

  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!timelineRef.current) return
    
    const rect = timelineRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const percentage = x / rect.width
    
    const timestamp = new Date(firstBlock.getTime() + (percentage * totalDuration * 1000))
    onTimeClick(timestamp)
  }

  const getCurrentPosition = () => {
    if (currentTime < firstBlock) return 0
    if (currentTime > lastBlock) return 100
    
    const elapsed = currentTime.getTime() - firstBlock.getTime()
    return (elapsed / (totalDuration * 1000)) * 100
  }

  const getRecordingBlocks = () => {
    return blocks.map((block, idx) => {
      const start = new Date(block.start_time)
      const end = new Date(block.end_time)
      
      const startOffset = (start.getTime() - firstBlock.getTime()) / 1000
      const duration = (end.getTime() - start.getTime()) / 1000
      
      const left = (startOffset / totalDuration) * 100
      const width = (duration / totalDuration) * 100
      
      return { left, width, key: idx, start, end }
    })
  }
  
  const getGapBlocks = () => {
    return gaps.map((gap, idx) => {
      const start = new Date(gap.start)
      const end = new Date(gap.end)
      
      const startOffset = (start.getTime() - firstBlock.getTime()) / 1000
      const duration = (end.getTime() - start.getTime()) / 1000
      
      const left = (startOffset / totalDuration) * 100
      const width = (duration / totalDuration) * 100
      
      return { left, width, key: idx, start, end }
    })
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="space-y-2">
      <div className="relative">
        {/* Time Labels */}
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>{formatTime(firstBlock)}</span>
          <span>{formatTime(lastBlock)}</span>
        </div>

        {/* Timeline Bar */}
        <div
          ref={timelineRef}
          onClick={handleTimelineClick}
          className="relative h-12 bg-gray-700 rounded-lg cursor-pointer overflow-hidden"
        >
          {/* Recording Blocks */}
          {getRecordingBlocks().map(block => (
            <div
              key={block.key}
              className="absolute top-0 h-full bg-blue-500 hover:bg-blue-600 transition-colors"
              style={{
                left: `${block.left}%`,
                width: `${block.width}%`,
              }}
              title={`${formatTime(block.start)} - ${formatTime(block.end)}`}
            />
          ))}
          
          {/* Gap Blocks */}
          {getGapBlocks().map(gap => (
            <div
              key={`gap-${gap.key}`}
              className="absolute top-0 h-full bg-red-900/50 border-x border-red-500"
              style={{
                left: `${gap.left}%`,
                width: `${gap.width}%`,
              }}
              title={`Gap: ${formatTime(gap.start)} - ${formatTime(gap.end)}`}
            />
          ))}

          {/* Current Time Indicator */}
          <div
            className="absolute top-0 w-0.5 h-full bg-red-500 z-10"
            style={{ left: `${getCurrentPosition()}%` }}
          >
            <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 bg-red-500 rounded-full" />
          </div>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-blue-500 rounded" />
            <span>Gravação ({blocks.length} blocos)</span>
          </div>
          {gaps.length > 0 && (
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-red-900/50 border border-red-500 rounded" />
              <span>Gaps ({gaps.length})</span>
            </div>
          )}
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 bg-red-500 rounded-full" />
            <span>Posição atual</span>
          </div>
        </div>
      </div>
    </div>
  )
}
