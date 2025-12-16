import React, { useState, useRef, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { 
  X, 
  Maximize2, 
  Minimize2, 
  Loader2, 
  Camera, 
  Menu, 
  MoreVertical 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import api from "@/lib/axios";
import { useToast } from "@/hooks/use-toast";
import VideoPlayer from "@/components/VideoPlayer";
import Timeline from "@/components/Timeline";
import CameraSideList from "@/components/CameraSideList";
import MapViewer, { Camera as MapCamera } from "@/components/MapViewer";
import { cn } from "@/lib/utils";

interface CameraType {
  id: number;
  name: string;
  location: string;
  latitude: number;
  longitude: number;
  status: "online" | "offline" | "lpr";
  thumbnail_url?: string | null;
  stream_url_frontend: string;
}

const mockTimelineEvents = [
  { startTime: 2, duration: 4, type: "continuous" as const },
  { startTime: 8.5, duration: 0.2, type: "motion" as const },
  { startTime: 13, duration: 2, type: "continuous" as const },
];

const LiveCameras: React.FC = () => {
  const [selectedCamera, setSelectedCamera] = useState<CameraType | null>(null);
  const [isPlayerExpanded, setIsPlayerExpanded] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false); // Controle manual da sidebar
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const { toast } = useToast();

  const { data: cameras = [], isLoading } = useQuery({
    queryKey: ['cameras'],
    queryFn: async () => {
      const response = await api.get("/cameras/");
      const raw = response.data;
      const list = Array.isArray(raw) ? raw : Array.isArray(raw?.results) ? raw.results : [];

      return list.map((c: any) => ({
        id: c.id,
        name: c.name,
        location: c.location || "Sem localização",
        latitude: Number(c.latitude ?? 0),
        longitude: Number(c.longitude ?? 0),
        status: c.status || "offline",
        thumbnail_url: c.thumbnail_url ?? c.thumbnail ?? null,
        stream_url_frontend: c.stream_url_frontend || "",
      })) as CameraType[];
    },
    staleTime: 1000 * 60 * 5,
  });

  const mapCameras: MapCamera[] = React.useMemo(() => cameras.map((c) => ({
    id: c.id,
    name: c.name,
    latitude: c.latitude,
    longitude: c.longitude,
    status: c.status,
  })), [cameras]);

  const handleCameraSelect = (cam: CameraType) => {
    setSelectedCamera(cam);
    setIsSidebarOpen(false); // Fecha sidebar ao selecionar para focar no vídeo
  };

  const handleSnapshot = () => {
    if (!videoRef.current || !selectedCamera) return;
    const video = videoRef.current;
    if (video.videoWidth === 0) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    
    if (ctx) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
      
      setSelectedCamera(prev => prev ? ({ ...prev, thumbnail_url: dataUrl }) : null);
      toast({ title: "Thumbnail atualizada", className: "bg-green-500 text-white border-none" });
    }
  };

  if (isLoading) {
    return <div className="h-full w-full bg-zinc-950 flex items-center justify-center">
      <Loader2 className="animate-spin text-white w-8 h-8"/>
    </div>;
  }

  return (
    <div className="h-full w-full relative bg-zinc-950 overflow-hidden">
      
      {/* 1. MAPA FULLSCREEN (Obrigatório) */}
      <div className="absolute inset-0 z-0">
        <MapViewer
          cameras={mapCameras}
          height="100%"
          onCameraClick={(mapCam) => {
            const fullCam = cameras.find((c) => c.id === mapCam.id);
            if (fullCam) handleCameraSelect(fullCam);
          }}
        />
      </div>

      {/* 2. SIDEBAR (Controlada pelo State) */}
      <Sheet open={isSidebarOpen} onOpenChange={setIsSidebarOpen}>
        <SheetContent side="left" className="p-0 w-[320px] bg-black/80 backdrop-blur-xl border-r border-white/10 text-white shadow-2xl">
            <div className="h-full pt-12 px-1"> 
            <CameraSideList 
                cameras={cameras} 
                selectedId={selectedCamera?.id} 
                onSelect={handleCameraSelect} 
            />
            </div>
        </SheetContent>
      </Sheet>

      {/* Botão Flutuante da Sidebar (Só aparece se não tiver câmera selecionada) */}
      {!selectedCamera && (
        <div className="absolute top-4 left-4 z-10 animate-in fade-in zoom-in duration-300">
            <Button 
                onClick={() => setIsSidebarOpen(true)}
                size="icon" 
                className="h-12 w-12 rounded-xl shadow-lg bg-black/80 hover:bg-black text-white border border-white/10"
            >
                <Menu className="h-6 w-6" />
            </Button>
        </div>
      )}

      {/* 3. PLAYER FLUTUANTE (O Design Solicitado) */}
      {selectedCamera && (
        <div 
          className={cn(
            "fixed transition-all duration-500 cubic-bezier(0.4, 0, 0.2, 1) z-50 overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)] border border-white/10 flex flex-col bg-zinc-900",
            // ESTADOS DE TAMANHO
            isPlayerExpanded 
              ? "inset-0 rounded-none" // Fullscreen
              : "top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[90%] md:w-[800px] h-[60vh] md:h-[550px] rounded-2xl" // Modal Flutuante
          )}
        >
            {/* HEADER DO PLAYER (Barra Escura) */}
            <div className="h-12 bg-black/90 backdrop-blur border-b border-white/10 flex items-center justify-between px-4 shrink-0">
                <div className="flex items-center gap-3">
                    {/* Botão UI/UX para abrir sidebar de dentro do player */}
                    <Button 
                        variant="ghost" 
                        size="icon" 
                        onClick={() => setIsSidebarOpen(true)}
                        className="text-white/70 hover:text-white hover:bg-white/10 -ml-2"
                    >
                        <Menu className="w-5 h-5" />
                    </Button>
                    
                    <div className="h-4 w-[1px] bg-white/10 mx-1" />

                    <div className="flex flex-col">
                        <span className="text-sm font-semibold text-white tracking-wide">{selectedCamera.name}</span>
                        <span className="text-[10px] text-zinc-400 font-mono uppercase tracking-wider">
                             {selectedCamera.status === 'online' ? 'Ao Vivo' : 'Offline'}
                        </span>
                    </div>
                </div>

                <div className="flex items-center gap-1">
                    <Button
                        variant="ghost"
                        size="icon"
                        className="text-white/70 hover:text-white hover:bg-white/10"
                        onClick={() => setIsPlayerExpanded(!isPlayerExpanded)}
                    >
                        {isPlayerExpanded ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="text-white/70 hover:text-red-400 hover:bg-red-500/10"
                        onClick={() => setSelectedCamera(null)}
                    >
                        <X className="w-5 h-5" />
                    </Button>
                </div>
            </div>

            {/* ÁREA DE VÍDEO (Fundo Preto) */}
            <div className="flex-1 relative bg-black group">
                <VideoPlayer
                    url={selectedCamera.stream_url_frontend}
                    poster={selectedCamera.thumbnail_url}
                    className="w-full h-full"
                    videoRefProp={videoRef}
                />
                
                {/* Overlay de Ações (Snapshot) */}
                <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button size="sm" onClick={handleSnapshot} className="bg-black/50 backdrop-blur hover:bg-black/70 text-white border border-white/10">
                        <Camera className="w-4 h-4 mr-2" /> Snapshot
                    </Button>
                </div>
            </div>

            {/* TIMELINE (Branca e Integrada no Rodapé) */}
            <div className="bg-white shrink-0 z-10 border-t border-zinc-200">
                <Timeline
                    currentTime={new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    duration={86400} // 24h em segundos
                    isPlaying={true}
                    onSeek={() => {}}
                    onTogglePlay={() => {}}
                    events={mockTimelineEvents}
                    // Passamos uma classe para remover bordas arredondadas e ajustar altura
                    className="border-none shadow-none h-auto py-1" 
                />
            </div>
        </div>
      )}
    </div>
  );
};

export default LiveCameras;