import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { Camera, Search, Signal, WifiOff } from "lucide-react";
import { Input } from "@/components/ui/input";

interface CameraType {
  id: number;
  name: string;
  status: string;
  location?: string;
  thumbnail_url?: string | null;
}

interface CameraSideListProps {
  cameras: CameraType[];
  selectedId?: number;
  onSelect: (camera: CameraType) => void;
}

const CameraSideList = ({ cameras, selectedId, onSelect }: CameraSideListProps) => {
  return (
    <div className="flex flex-col h-full w-full">
      
      {/* HEADER & SEARCH - Visual Clean */}
      <div className="pb-6 px-4 space-y-4">
        <div>
            <h3 className="text-lg font-bold text-white tracking-tight">Câmeras</h3>
            <p className="text-xs text-white/50 font-medium">Monitoramento em tempo real</p>
        </div>

        <div className="relative group">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-white/40 group-focus-within:text-white/80 transition-colors" />
          <Input 
              placeholder="Buscar câmera..." 
              className="pl-9 bg-white/5 border-white/10 text-white placeholder:text-white/30 focus-visible:ring-1 focus-visible:ring-white/20 focus-visible:border-white/20 rounded-xl h-10 transition-all hover:bg-white/10" 
          />
        </div>
      </div>
      
      <ScrollArea className="flex-1 px-2 -mr-2 pr-4"> {/* Ajuste de margem para o scrollbar não colar */}
        <div className="flex flex-col gap-2 pb-4">
          {cameras.map((camera) => {
            const isSelected = selectedId === camera.id;
            const isOnline = camera.status === 'online';
            
            return (
              <div
                key={camera.id}
                onClick={() => onSelect(camera)}
                className={cn(
                  "group relative flex gap-3 p-2.5 rounded-xl cursor-pointer transition-all duration-300 border border-transparent",
                  // Efeitos de Hover e Seleção Profissionais
                  isSelected 
                    ? "bg-white/10 border-white/10 shadow-[0_0_15px_rgba(0,0,0,0.2)]" 
                    : "hover:bg-white/5 hover:border-white/5"
                )}
              >
                {/* Indicador de Seleção (Barra lateral) */}
                {isSelected && (
                    <div className="absolute left-0 top-3 bottom-3 w-1 bg-blue-500 rounded-r-full shadow-[0_0_10px_#3b82f6]" />
                )}

                {/* THUMBNAIL - Aspecto Moderno */}
                <div className="relative w-24 h-16 shrink-0 bg-black/40 rounded-lg overflow-hidden border border-white/5 group-hover:border-white/20 transition-colors">
                  {camera.thumbnail_url ? (
                    <img 
                      src={camera.thumbnail_url} 
                      alt={camera.name} 
                      className="w-full h-full object-cover opacity-70 group-hover:opacity-100 transition-opacity duration-500"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-white/20 group-hover:text-white/40 transition-colors">
                      <Camera className="h-6 w-6" />
                    </div>
                  )}
                  
                  {/* Badge de Status Minimalista */}
                  <div className="absolute bottom-1 right-1">
                      {isOnline ? (
                        <div className="flex items-center justify-center w-4 h-4 rounded-full bg-black/60 backdrop-blur-sm border border-green-500/50">
                            <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_5px_#22c55e]" />
                        </div>
                      ) : (
                         <div className="flex items-center justify-center w-4 h-4 rounded-full bg-black/60 backdrop-blur-sm border border-red-500/50">
                            <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
                        </div>
                      )}
                  </div>
                </div>

                {/* INFO - Tipografia Clean */}
                <div className="flex flex-col justify-center min-w-0 flex-1 py-0.5 pl-1">
                  <div className="flex items-center justify-between">
                      <h4 className={cn(
                        "font-medium text-sm leading-tight truncate transition-colors",
                        isSelected ? "text-white" : "text-white/80 group-hover:text-white"
                      )}>
                        {camera.name}
                      </h4>
                  </div>
                  
                  <p className="text-[11px] text-white/40 truncate mt-1 group-hover:text-white/60 transition-colors">
                    {camera.location || "Localização não definida"}
                  </p>

                  <div className="flex items-center gap-2 mt-1.5">
                    {isOnline ? (
                        <div className="flex items-center gap-1 text-[10px] font-medium text-green-400/90 bg-green-500/10 px-1.5 py-0.5 rounded text-xs w-fit">
                            <Signal className="w-3 h-3" /> <span>ONLINE</span>
                        </div>
                    ) : (
                        <div className="flex items-center gap-1 text-[10px] font-medium text-red-400/90 bg-red-500/10 px-1.5 py-0.5 rounded text-xs w-fit">
                            <WifiOff className="w-3 h-3" /> <span>OFFLINE</span>
                        </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
};

export default CameraSideList;