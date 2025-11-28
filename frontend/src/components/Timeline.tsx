import { useState, useRef, MouseEvent } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Calendar as CalendarIcon, Clock, Save, Pause, Play } from 'lucide-react';
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

interface TimelineProps {
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  status: 'online' | 'offline' | 'loading'; // Novo prop de status
  onSeek: (time: number) => void;
  onTogglePlay: () => void;
  onSaveClip?: () => void;
  className?: string;
}

const Timeline = ({ 
  currentTime, 
  duration, 
  isPlaying,
  status,
  onSeek,
  onTogglePlay,
  onSaveClip,
  className 
}: TimelineProps) => {
  const [zoomLevel, setZoomLevel] = useState<'24h' | '1h' | '5m'>('24h');
  const progressBarRef = useRef<HTMLDivElement>(null);

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  const formatTime = (seconds: number) => {
    if (!seconds || isNaN(seconds)) return "00h00";
    const date = new Date(0);
    date.setSeconds(seconds);
    return date.toISOString().substr(11, 5).replace(':', 'h');
  };

  const handleSeek = (e: MouseEvent<HTMLDivElement>) => {
    if (!progressBarRef.current || duration <= 0) return;
    const rect = progressBarRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(1, x / rect.width));
    onSeek(percentage * duration);
  };

  // Configuração visual do status
  const statusConfig = {
    online: { label: 'Online', color: 'bg-green-100 text-green-700 border-green-200', dot: 'bg-green-500' },
    offline: { label: 'Offline', color: 'bg-red-100 text-red-700 border-red-200', dot: 'bg-red-500' },
    loading: { label: 'Conectando...', color: 'bg-yellow-100 text-yellow-700 border-yellow-200', dot: 'bg-yellow-500 animate-pulse' }
  };
  
  const currentStatus = statusConfig[status] || statusConfig.offline;

  return (
    <div className={cn("flex flex-col w-full bg-white md:rounded-b-xl border-t shadow-sm select-none", className)}>
      
      {/* Toolbar - Responsiva */}
      <div className="flex items-center justify-between px-3 md:px-6 py-2 md:py-4 border-b">
        <div className="flex items-center gap-2 md:gap-4">
          {/* Botão Play - Sempre visível */}
          <Button size="icon" variant="ghost" className="h-8 w-8 text-slate-700 shrink-0" onClick={onTogglePlay}>
             {isPlaying ? <Pause className="h-5 w-5 fill-current" /> : <Play className="h-5 w-5 fill-current" />}
          </Button>

          {/* Zoom - Escondido em telas muito pequenas, visível em tablets/desktop */}
          <ToggleGroup type="single" value={zoomLevel} onValueChange={(v) => v && setZoomLevel(v as any)} className="hidden sm:flex bg-gray-100 p-1 rounded-lg">
            {[{v:'24h', l:'24h'}, {v:'1h', l:'1h'}, {v:'5m', l:'5m'}].map((item) => (
               <ToggleGroupItem 
                 key={item.v} value={item.v} 
                 className="px-3 py-1 h-7 text-xs font-medium rounded-md data-[state=on]:bg-white data-[state=on]:shadow-sm data-[state=on]:text-gray-900 text-gray-500 transition-all"
               >
                 {item.l}
               </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </div>

        <Button 
            onClick={onSaveClip}
            className="bg-blue-600 hover:bg-blue-700 text-white h-8 md:h-9 px-3 md:px-6 rounded-md text-xs md:text-sm font-medium shadow-sm transition-transform active:scale-95"
        >
            <Save className="w-4 h-4 mr-2 hidden sm:inline" />
            Salvar <span className="hidden sm:inline ml-1">vídeo</span>
        </Button>
      </div>

      {/* Área da Régua */}
      <div className="relative w-full h-20 md:h-28 px-4 md:px-8 flex flex-col justify-center bg-white">
        <div 
            ref={progressBarRef}
            className="relative h-2 md:h-2.5 w-full bg-gray-200 rounded-full cursor-pointer group touch-none mb-2"
            onClick={handleSeek}
        >
            <div 
                className="absolute top-0 left-0 h-full bg-blue-600 rounded-l-full transition-all duration-75"
                style={{ width: `${progress}%` }}
            >
                <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 w-4 h-4 md:w-5 md:h-5 bg-white border-2 border-blue-600 rounded-full shadow-md scale-100 md:scale-90 md:group-hover:scale-110 transition-transform z-10" />
            </div>
        </div>

        <div className="flex justify-between text-[10px] md:text-xs text-gray-400 font-medium mt-1">
            <span>00h00</span>
            <span>12h00</span>
            <span>24h00</span>
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between px-4 md:px-6 py-2 md:py-3 bg-gray-50 md:rounded-b-xl border-t text-xs text-gray-600">
        <div className="flex items-center gap-3 md:gap-4">
            <div className="flex items-center gap-2">
                <Clock className="w-3.5 h-3.5 text-gray-400" />
                <span className="hidden sm:inline">{format(new Date(), "dd/MM/yyyy", { locale: ptBR })},</span> 
                <span className="font-mono">{new Date().toLocaleTimeString().slice(0,5)}</span>
            </div>
            
            {/* Status Dinâmico */}
            <div className={cn("px-2 py-0.5 rounded-full font-bold text-[10px] border uppercase tracking-wide flex items-center gap-1.5 transition-colors", currentStatus.color)}>
                <div className={cn("w-1.5 h-1.5 rounded-full", currentStatus.dot)} />
                {currentStatus.label}
            </div>
        </div>

        <Button variant="ghost" size="sm" className="h-auto p-0 text-blue-600 hover:text-blue-700 hover:bg-transparent font-medium gap-1.5">
            <CalendarIcon className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Alterar Data</span>
            <span className="sm:hidden">Data</span>
        </Button>
      </div>
    </div>
  );
};

export default Timeline;