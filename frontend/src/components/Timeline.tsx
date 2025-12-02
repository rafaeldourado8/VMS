// VMS/frontend/src/components/Timeline.tsx
import { useState, useRef, MouseEvent } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Calendar as CalendarIcon, Clock, Save, Pause, Play, Scissors } from 'lucide-react';
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { ClipTrimmer } from './ClipTrimmer'; // Importe o componente criado

interface TimelineProps {
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  onSeek: (time: number) => void;
  onTogglePlay: () => void;
  onSaveClip?: (start: number, end: number) => void;
  className?: string;
}

const Timeline = ({ 
  currentTime, 
  duration, 
  isPlaying,
  onSeek,
  onTogglePlay,
  onSaveClip,
  className 
}: TimelineProps) => {
  const [zoomLevel, setZoomLevel] = useState<'24h' | '1h' | '5m'>('24h');
  const [isClipMode, setIsClipMode] = useState(false);
  // Range inicial de recorte (ex: 20% a 80%)
  const [clipRange, setClipRange] = useState({ start: 20, end: 80 }); 
  
  const progressBarRef = useRef<HTMLDivElement>(null);
  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  const handleSeek = (e: MouseEvent<HTMLDivElement>) => {
    if (!progressBarRef.current || duration <= 0) return;
    const rect = progressBarRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, x / rect.width));
    onSeek(percentage * duration);
  };

  const handleSaveClick = () => {
    if (!isClipMode) {
      setIsClipMode(true);
      // Pausa o vídeo para facilitar a edição
      if (isPlaying) onTogglePlay();
    } else {
      // Confirma o salvamento
      const startSec = (clipRange.start / 100) * duration;
      const endSec = (clipRange.end / 100) * duration;
      onSaveClip?.(startSec, endSec);
      setIsClipMode(false);
    }
  };

  return (
    <div className={cn("flex flex-col w-full bg-white border-t shadow-sm select-none", className)}>
      
      {/* Toolbar */}
      <div className="flex items-center justify-between px-3 md:px-6 py-2 border-b h-12">
        <div className="flex items-center gap-2">
          <Button size="icon" variant="ghost" className="h-8 w-8 text-slate-700" onClick={onTogglePlay}>
             {isPlaying ? <Pause className="h-4 w-4 fill-current" /> : <Play className="h-4 w-4 fill-current" />}
          </Button>

          <ToggleGroup type="single" value={zoomLevel} onValueChange={(v) => v && setZoomLevel(v as any)} className="hidden sm:flex">
            {['24h', '1h', '5m'].map((l) => (
               <ToggleGroupItem key={l} value={l} className="h-7 text-xs px-2">{l}</ToggleGroupItem>
            ))}
          </ToggleGroup>
        </div>

        <Button 
            onClick={handleSaveClick}
            variant={isClipMode ? "default" : "secondary"}
            className={cn("h-8 text-xs font-medium gap-2", isClipMode && "bg-yellow-500 hover:bg-yellow-600 text-black")}
        >
            {isClipMode ? <Save className="w-3.5 h-3.5" /> : <Scissors className="w-3.5 h-3.5" />}
            {isClipMode ? "Confirmar Recorte" : "Salvar Clipe"}
        </Button>
      </div>

      {/* Régua / Barra de Progresso */}
      <div className="relative w-full h-20 px-6 flex flex-col justify-center bg-gray-50/50">
        <div 
            ref={progressBarRef}
            className="relative h-3 w-full bg-gray-200 rounded-full cursor-pointer group touch-none"
            onClick={handleSeek}
        >
            {/* Barra de Progresso */}
            <div 
                className="absolute top-0 left-0 h-full bg-blue-500 rounded-l-full transition-all duration-75"
                style={{ width: `${progress}%` }}
            />
            
            {/* Knob do Player */}
            <div 
                className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-white border-2 border-blue-500 rounded-full shadow-md z-30"
                style={{ left: `${progress}%`, transform: 'translate(-50%, -50%)' }} 
            />

            {/* Componente de Recorte Isolado */}
            {isClipMode && <ClipTrimmer range={clipRange} />}
        </div>

        {/* Marcações de Tempo */}
        <div className="flex justify-between text-[10px] text-gray-400 font-medium mt-2">
            <span>00:00</span>
            <span>12:00</span>
            <span>23:59</span>
        </div>
      </div>

      {/* Footer / Info */}
      <div className="flex items-center justify-between px-6 py-2 bg-white border-t text-xs text-gray-500">
        <div className="flex items-center gap-2">
            <Clock className="w-3.5 h-3.5" />
            <span>{format(new Date(), "dd/MM/yyyy HH:mm", { locale: ptBR })}</span> 
        </div>
        <Button variant="link" size="sm" className="h-auto p-0 text-xs">
            <CalendarIcon className="w-3.5 h-3.5 mr-1" /> Alterar Data
        </Button>
      </div>
    </div>
  );
};

export default Timeline;