import { useState, useRef, MouseEvent } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Calendar as CalendarIcon, Clock, Save, Pause, Play, Scissors, ChevronDown } from 'lucide-react';
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { ClipTrimmer } from './ClipTrimmer';

interface TimelineProps {
  currentTime: string; // Simplifiquei para string visual por enquanto
  duration?: number;
  isPlaying?: boolean;
  onSeek?: (time: number) => void;
  onTogglePlay?: () => void;
  onSaveClip?: (start: number, end: number) => void;
  events?: any[];
  className?: string;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
}

const Timeline = ({ 
  currentTime, 
  isPlaying,
  onTogglePlay,
  className 
}: TimelineProps) => {
  const [zoomLevel, setZoomLevel] = useState<'24h' | '1h' | '5m'>('24h');
  
  // Design Limpo e Branco (Conforme solicitado)
  return (
    <div className={cn("flex flex-col w-full bg-white text-zinc-800 select-none", className)}>
      
      {/* 1. Controles Superiores */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-zinc-100">
        <div className="flex items-center gap-3">
          <Button 
            size="icon" 
            variant="outline" 
            className="h-8 w-8 rounded-full border-zinc-300 hover:bg-zinc-100 hover:text-blue-600" 
            onClick={onTogglePlay}
          >
             {isPlaying ? <Pause className="h-3.5 w-3.5 fill-current" /> : <Play className="h-3.5 w-3.5 fill-current" />}
          </Button>

          <div className="hidden sm:flex bg-zinc-100 rounded-lg p-0.5">
            {['24h', '1h', '5m'].map((l) => (
              <Button
                key={l}
                size="sm"
                variant="ghost"
                className={cn(
                    "h-6 text-[10px] px-3 rounded-md transition-all",
                    zoomLevel === l ? "bg-white shadow-sm text-zinc-900 font-bold" : "text-zinc-500 hover:text-zinc-700"
                )}
                onClick={() => setZoomLevel(l as any)}
              >
                {l}
              </Button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-medium text-zinc-500">
             <div className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-blue-500" />
                <span className="text-zinc-900">{currentTime}</span>
             </div>
             <div className="h-3 w-[1px] bg-zinc-300" />
             <div className="flex items-center gap-1.5 cursor-pointer hover:text-blue-600">
                <CalendarIcon className="w-3.5 h-3.5" />
                <span>Hoje</span>
                <ChevronDown className="w-3 h-3 opacity-50" />
             </div>
        </div>
      </div>

      {/* 2. Área da Régua (Visual Profissional) */}
      <div className="relative w-full h-16 bg-zinc-50/50 flex flex-col justify-center px-4">
        {/* Linha base */}
        <div className="absolute top-1/2 left-0 right-0 h-[2px] bg-zinc-200" />

        {/* Marcadores de Tempo (Fake para visual) */}
        <div className="absolute inset-0 flex justify-between items-center px-4 pointer-events-none opacity-30">
             {[...Array(12)].map((_, i) => <div key={i} className="h-full w-[1px] bg-zinc-400" />)}
        </div>

        {/* Indicador de "Agora" (Agulha) */}
        <div className="absolute top-0 bottom-0 left-1/2 w-[2px] bg-red-500 z-10 shadow-[0_0_10px_rgba(239,68,68,0.5)]">
             <div className="absolute top-0 -translate-x-1/2 -mt-1 w-0 h-0 border-l-[4px] border-l-transparent border-r-[4px] border-r-transparent border-t-[6px] border-t-red-500" />
        </div>

        {/* Barra de Eventos (Exemplo) */}
        <div className="relative h-4 w-full bg-zinc-200/50 rounded-full overflow-hidden mt-1">
             <div className="absolute left-[20%] width-[30%] h-full bg-blue-400/30" />
             <div className="absolute left-[60%] width-[5%] h-full bg-blue-600" />
        </div>
      </div>
    </div>
  );
};

export default Timeline;