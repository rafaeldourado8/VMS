import React, { useRef, useEffect, useState } from 'react';

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
}

export const CanvasTimeline: React.FC<CanvasTimelineProps> = ({
  segments,
  currentTime,
  onSeek,
  height = 120
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Janela de visualização (Viewport) - Default: Tempo atual +/- 30 minutos
  const [viewWindow, setViewWindow] = useState({
    start: currentTime.getTime() - 30 * 60 * 1000, 
    end: currentTime.getTime() + 30 * 60 * 1000    
  });

  const [isDragging, setIsDragging] = useState(false);
  const [lastX, setLastX] = useState(0);

  // Conversão: Pixel <-> Tempo
  const xToTime = (x: number, width: number) => {
    const range = viewWindow.end - viewWindow.start;
    return viewWindow.start + (x * (range / width));
  };

  const timeToX = (time: number, width: number) => {
    const range = viewWindow.end - viewWindow.start;
    return ((time - viewWindow.start) / range) * width;
  };

  // Renderização principal
  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = container.getBoundingClientRect();
    
    // Ajuste de DPI para nitidez
    canvas.width = rect.width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${rect.width}px`;
    canvas.style.height = `${height}px`;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    ctx.scale(dpr, dpr);
    const width = rect.width;

    // 1. Fundo
    ctx.fillStyle = '#111827'; // gray-900 (Tailwind)
    ctx.fillRect(0, 0, width, height);

    // 2. Grid de Tempo (Dinâmico)
    const range = viewWindow.end - viewWindow.start;
    // Lógica para decidir intervalo dos ticks (ex: 1min, 5min, 1h)
    let tickInterval = 60 * 1000; 
    if (range > 12 * 3600 * 1000) tickInterval = 2 * 3600 * 1000;
    else if (range > 6 * 3600 * 1000) tickInterval = 3600 * 1000;
    else if (range > 3600 * 1000) tickInterval = 30 * 60 * 1000;
    else if (range > 60 * 60 * 1000) tickInterval = 10 * 60 * 1000;
    else if (range > 15 * 60 * 1000) tickInterval = 5 * 60 * 1000;

    ctx.strokeStyle = '#374151'; // gray-700
    ctx.fillStyle = '#9CA3AF'; // gray-400
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'center';
    ctx.lineWidth = 1;

    const firstTick = Math.ceil(viewWindow.start / tickInterval) * tickInterval;

    for (let t = firstTick; t < viewWindow.end; t += tickInterval) {
      const x = timeToX(t, width);
      
      // Linha vertical
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();

      // Texto do horário
      const date = new Date(t);
      const label = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      ctx.fillText(label, x, height - 8);
    }

    // 3. Segmentos de Gravação
    // Filtra apenas o que está visível para performance
    const visibleSegments = segments.filter(s => 
      s.end.getTime() > viewWindow.start && s.start.getTime() < viewWindow.end
    );

    visibleSegments.forEach(seg => {
      const xStart = Math.max(0, timeToX(seg.start.getTime(), width));
      const xEnd = Math.min(width, timeToX(seg.end.getTime(), width));
      const segWidth = Math.max(1, xEnd - xStart);

      ctx.fillStyle = seg.type === 'motion' ? '#EF4444' : '#3B82F6'; // red-500 : blue-500
      
      // Desenha barra arredondada centralizada verticalmente
      const barHeight = height * 0.4;
      const barY = (height - barHeight) / 2;
      ctx.fillRect(xStart, barY, segWidth, barHeight);
    });

    // 4. Playhead (Agulha)
    const playheadX = timeToX(currentTime.getTime(), width);
    
    // Linha da agulha
    ctx.beginPath();
    ctx.strokeStyle = '#EAB308'; // yellow-500
    ctx.lineWidth = 2;
    ctx.moveTo(playheadX, 0);
    ctx.lineTo(playheadX, height);
    ctx.stroke();

    // Cabeça da agulha (triângulo invertido)
    ctx.fillStyle = '#EAB308';
    ctx.beginPath();
    ctx.moveTo(playheadX - 6, 0);
    ctx.lineTo(playheadX + 6, 0);
    ctx.lineTo(playheadX, 8);
    ctx.fill();

  }, [segments, viewWindow, currentTime, height]);

  // --- Controles (Zoom e Pan) ---

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY > 0 ? 1.1 : 0.9;
    const range = viewWindow.end - viewWindow.start;
    const newRange = range * zoomFactor;

    // Limites de zoom (min 1 min, max 24h)
    if (newRange < 60 * 1000 || newRange > 24 * 3600 * 1000) return;

    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseTime = xToTime(mouseX, rect.width);
    
    // Zoom focado na posição do mouse (zoom to cursor)
    const mouseRatio = mouseX / rect.width;
    const newStart = mouseTime - (newRange * mouseRatio);
    
    setViewWindow({ start: newStart, end: newStart + newRange });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setLastX(e.clientX);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      const deltaX = e.clientX - lastX;
      setLastX(e.clientX);

      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const range = viewWindow.end - viewWindow.start;
      const deltaMs = (deltaX / rect.width) * range;

      setViewWindow(prev => ({
        start: prev.start - deltaMs, // Inverte para arrastar "o papel"
        end: prev.end - deltaMs
      }));
    }
  };

  const handleMouseUp = (e: React.MouseEvent) => {
    // Detecta clique vs arraste (se moveu menos de 5px, é clique)
    if (isDragging && Math.abs(e.clientX - lastX) < 5) {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const clickTime = xToTime(e.clientX - rect.left, rect.width);
      onSeek(new Date(clickTime));
    }
    setIsDragging(false);
  };

  return (
    <div 
      ref={containerRef}
      className="relative w-full cursor-grab active:cursor-grabbing overflow-hidden bg-gray-900 border-t border-gray-800"
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={() => setIsDragging(false)}
    >
      <canvas ref={canvasRef} />
      
      {/* Botão de Reset Zoom Flutuante */}
      <button 
        className="absolute bottom-2 right-2 bg-gray-800/80 text-white text-xs px-2 py-1 rounded hover:bg-gray-700 transition-colors backdrop-blur-sm border border-gray-700"
        onClick={() => setViewWindow({
            start: currentTime.getTime() - 15 * 60 * 1000,
            end: currentTime.getTime() + 15 * 60 * 1000
        })}
      >
        Centralizar
      </button>
    </div>
  );
};