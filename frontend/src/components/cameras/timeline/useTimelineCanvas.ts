import { useEffect } from 'react';
import { TimelineSegment } from '../CanvasTimeline';
import { timeToX, getTimeIntervals } from './timelineUtils';

interface TimelineCanvasProps {
  canvasRef: React.RefObject<HTMLCanvasElement>;
  containerRef: React.RefObject<HTMLDivElement>;
  segments: TimelineSegment[];
  currentTime: Date;
  viewWindow: { start: number; end: number };
  timeFilter: { start: string; end: string } | null;
  height: number;
  clipSelection?: { start: Date | null; end: Date | null };
}

export const useTimelineCanvas = ({
  canvasRef,
  containerRef,
  segments,
  currentTime,
  viewWindow,
  timeFilter,
  height,
  clipSelection
}: TimelineCanvasProps) => {
  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = container.getBoundingClientRect();
    
    canvas.width = rect.width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${height}px`;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.scale(dpr, dpr);
    const width = rect.width;

    // Fundo limpo
    ctx.fillStyle = '#18181B';
    ctx.fillRect(0, 0, width, height);

    const trackHeight = 6;
    const trackY = height / 2 - trackHeight / 2;

    // Trilho base minimalista
    ctx.fillStyle = '#27272A';
    ctx.fillRect(0, trackY, width, trackHeight);

    // Grid e labels
    const range = viewWindow.end - viewWindow.start;
    const { major } = getTimeIntervals(range);

    ctx.font = '500 10px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.textAlign = 'center';

    const firstMajor = Math.ceil(viewWindow.start / major) * major;
    for (let t = firstMajor; t < viewWindow.end; t += major) {
      const x = timeToX(t, width, viewWindow.start, viewWindow.end);
      
      // Tick mark
      ctx.fillStyle = '#52525B';
      ctx.fillRect(x - 0.5, trackY - 4, 1, 4);
      
      // Label
      const date = new Date(t);
      const label = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      ctx.fillStyle = '#A1A1AA';
      ctx.fillText(label, x, trackY - 8);
    }

    // Segmentos
    let visibleSegments = segments.filter(s => 
      s.end.getTime() > viewWindow.start && s.start.getTime() < viewWindow.end
    );

    if (timeFilter) {
      visibleSegments = visibleSegments.filter(seg => {
        const segStart = new Date(seg.start);
        const segTime = segStart.getHours() * 60 + segStart.getMinutes();
        const [startH, startM] = timeFilter.start.split(':').map(Number);
        const [endH, endM] = timeFilter.end.split(':').map(Number);
        const filterStart = startH * 60 + startM;
        const filterEnd = endH * 60 + endM;
        return segTime >= filterStart && segTime <= filterEnd;
      });
    }

    visibleSegments.forEach((seg) => {
      const xStart = Math.max(0, timeToX(seg.start.getTime(), width, viewWindow.start, viewWindow.end));
      const xEnd = Math.min(width, timeToX(seg.end.getTime(), width, viewWindow.start, viewWindow.end));
      const segWidth = Math.max(2, xEnd - xStart);

      ctx.fillStyle = seg.type === 'motion' ? '#10B981' : '#3B82F6';
      ctx.fillRect(xStart, trackY, segWidth, trackHeight);
    });

    // Seleção de clip
    if (clipSelection?.start && clipSelection?.end) {
      const startX = timeToX(clipSelection.start.getTime(), width, viewWindow.start, viewWindow.end);
      const endX = timeToX(clipSelection.end.getTime(), width, viewWindow.start, viewWindow.end);
      const selWidth = Math.abs(endX - startX);
      const selX = Math.min(startX, endX);

      ctx.fillStyle = 'rgba(168, 85, 247, 0.2)';
      ctx.fillRect(selX, 0, selWidth, height);
      
      ctx.strokeStyle = '#A855F7';
      ctx.lineWidth = 2;
      ctx.strokeRect(selX, 0, selWidth, height);
    }

    // Playhead
    const playheadX = timeToX(currentTime.getTime(), width, viewWindow.start, viewWindow.end);
    
    // Linha vertical
    ctx.fillStyle = '#60A5FA';
    ctx.fillRect(playheadX - 1, trackY, 2, trackHeight);
    
    // Handle circular
    ctx.fillStyle = '#60A5FA';
    ctx.beginPath();
    ctx.arc(playheadX, trackY + trackHeight / 2, 6, 0, Math.PI * 2);
    ctx.fill();
    
    // Borda branca
    ctx.strokeStyle = '#FFFFFF';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Tooltip com tempo atual (apenas se houver espaço)
    if (height > 50) {
      const timeLabel = currentTime.toLocaleTimeString('pt-BR');
      ctx.font = '600 10px -apple-system, BlinkMacSystemFont, sans-serif';
      ctx.textAlign = 'center';
      const labelWidth = ctx.measureText(timeLabel).width + 12;
      
      ctx.fillStyle = '#18181B';
      ctx.beginPath();
      ctx.roundRect(playheadX - labelWidth / 2, trackY + 14, labelWidth, 20, 4);
      ctx.fill();
      
      ctx.strokeStyle = '#3F3F46';
      ctx.lineWidth = 1;
      ctx.stroke();
      
      ctx.fillStyle = '#FFFFFF';
      ctx.fillText(timeLabel, playheadX, trackY + 27);
    }

  }, [segments, viewWindow, currentTime, height, timeFilter, clipSelection]);
};
