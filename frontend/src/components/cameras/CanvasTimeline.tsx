import React, { useRef, useState, useCallback } from 'react';
import { useTimelineState } from './timeline/useTimelineState';
import { useTimelineCanvas } from './timeline/useTimelineCanvas';
import { TimeFilter } from './timeline/TimeFilter';
import { xToTime } from './timeline/timelineUtils';

export interface TimelineSegment {
  start: Date;
  end: Date;
  type: 'continuous' | 'motion';
}

interface CanvasTimelineProps {
  segments: TimelineSegment[];
  currentTime: Date;
  onSeek: (time: Date) => void;
  height?: number;
  clipSelection?: { start: Date | null; end: Date | null };
  timeFilter?: { start: string; end: string } | null;
}

export const CanvasTimeline: React.FC<CanvasTimelineProps> = ({
  segments,
  currentTime,
  onSeek,
  height = 120,
  clipSelection,
  timeFilter: externalTimeFilter
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isDraggingPlayhead, setIsDraggingPlayhead] = useState(false);
  const seekTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const state = useTimelineState(currentTime);

  const debouncedSeek = useCallback((time: Date) => {
    if (seekTimeoutRef.current) {
      clearTimeout(seekTimeoutRef.current);
    }
    seekTimeoutRef.current = setTimeout(() => {
      onSeek(time);
    }, 16); // ~60fps
  }, [onSeek]);

  useTimelineCanvas({
    canvasRef,
    containerRef,
    segments,
    currentTime,
    viewWindow: state.viewWindow,
    timeFilter: externalTimeFilter,
    height,
    clipSelection
  });

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const range = state.viewWindow.end - state.viewWindow.start;
    const newRange = range * (e.deltaY > 0 ? 1.1 : 0.9);

    if (newRange < 60 * 1000 || newRange > 24 * 3600 * 1000) return;

    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseTime = xToTime(mouseX, rect.width, state.viewWindow.start, state.viewWindow.end);
    const mouseRatio = mouseX / rect.width;
    const newStart = mouseTime - (newRange * mouseRatio);
    
    state.setViewWindow({ start: newStart, end: newStart + newRange });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseTime = xToTime(mouseX, rect.width, state.viewWindow.start, state.viewWindow.end);
    const playheadX = ((currentTime.getTime() - state.viewWindow.start) / (state.viewWindow.end - state.viewWindow.start)) * rect.width;
    
    // Se clicou perto da bolinha (±10px), arrasta a bolinha
    if (Math.abs(mouseX - playheadX) < 10) {
      setIsDraggingPlayhead(true);
      debouncedSeek(new Date(mouseTime));
      return;
    }
    
    state.setIsDragging(true);
    state.setLastX(e.clientX);
    state.setAutoFollow(false);
    state.setDragStartX(e.clientX);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseTime = xToTime(mouseX, rect.width, state.viewWindow.start, state.viewWindow.end);
    state.setHoverTime(new Date(mouseTime));
    state.setHoverX(mouseX);

    // Se está arrastando a bolinha
    if (isDraggingPlayhead) {
      debouncedSeek(new Date(mouseTime));
      return;
    }

    if (state.isDragging) {
      const dragDistance = Math.abs(e.clientX - state.dragStartX);
      
      // Se arrastou mais de 10px, é um drag (pan)
      if (dragDistance > 10) {
        const deltaX = e.clientX - state.lastX;
        state.setLastX(e.clientX);
        const range = state.viewWindow.end - state.viewWindow.start;
        const deltaMs = (deltaX / rect.width) * range;
        state.setViewWindow(prev => ({ start: prev.start - deltaMs, end: prev.end - deltaMs }));
      }
    }
  };

  const handleMouseUp = (e: React.MouseEvent) => {
    if (isDraggingPlayhead) {
      setIsDraggingPlayhead(false);
      return;
    }
    
    const dragDistance = Math.abs(e.clientX - state.dragStartX);
    
    // Se arrastou menos de 10px, é um clique
    if (dragDistance < 10) {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const clickTime = xToTime(e.clientX - rect.left, rect.width, state.viewWindow.start, state.viewWindow.end);
      debouncedSeek(new Date(clickTime));
    }
    
    state.setIsDragging(false);
  };

  return (
    <div 
      ref={containerRef}
      className="relative w-full overflow-hidden bg-gray-800"
      style={{ cursor: isDraggingPlayhead ? 'grabbing' : 'grab' }}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={() => {
        state.setIsDragging(false);
        setIsDraggingPlayhead(false);
        state.setHoverTime(null);
      }}
    >
      <canvas ref={canvasRef} />
      
      {state.hoverTime && (
        <div 
          className="absolute top-3 bg-gray-900 text-white text-xs px-2 py-1 rounded-md pointer-events-none font-mono"
          style={{ left: `${state.hoverX}px`, transform: 'translateX(-50%)' }}
        >
          {state.hoverTime.toLocaleTimeString('pt-BR')}
        </div>
      )}
    </div>
  );
};
