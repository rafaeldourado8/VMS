import React, { useState, useRef } from "react";
import { useQuery } from "@tanstack/react-query"; // Importação para Cache
import { List, X, Maximize2, Minimize2, Loader2, Camera } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
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
  { startTime: 14.5, duration: 0.3, type: "motion" as const },
  { startTime: 18, duration: 5, type: "continuous" as const },
];

const glassSheetClasses = "bg-black/30 backdrop-blur-xl border-r border-white/10 text-white shadow-2xl";

const LiveCameras: React.FC = () => {
  const [selectedCamera, setSelectedCamera] = useState<CameraType | null>(null);
  const [isPlayerExpanded, setIsPlayerExpanded] = useState(false);
  const [isTimelineExpanded, setIsTimelineExpanded] = useState(false);
  
  // Referência para acessar o elemento <video> diretamente
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const { toast } = useToast();

  // Otimização: Cache compartilhado com o Dashboard via React Query
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

  // Memoização para evitar recálculo de array em cada render
  const mapCameras: MapCamera[] = React.useMemo(() => cameras.map((c) => ({
    id: c.id,
    name: c.name,
    location: c.location,
    latitude: c.latitude,
    longitude: c.longitude,
    status: c.status,
    thumbnail_url: c.thumbnail_url,
  })), [cameras]);

  const handleCameraSelect = (cam: CameraType) => {
    setSelectedCamera(cam);
  };

  const handleClosePlayer = () => {
    setSelectedCamera(null);
    setIsPlayerExpanded(false);
    setIsTimelineExpanded(false);
  };

  // Função para tirar a foto (snapshot) da stream
  const handleSnapshot = () => {
    if (!videoRef.current || !selectedCamera) return;

    const video = videoRef.current;
    
    // Verifica se o vídeo tem dimensões válidas
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      toast({
        title: "Erro ao capturar",
        description: "Aguarde o vídeo carregar antes de atualizar a thumb.",
        variant: "destructive"
      });
      return;
    }

    // Cria um canvas temporário
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext("2d");
    if (ctx) {
      // Desenha o frame atual do vídeo no canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      try {
        // Converte para Base64 (JPG com 90% de qualidade)
        const dataUrl = canvas.toDataURL("image/jpeg", 0.9);

        // Atualiza o estado visual localmente
        setSelectedCamera(prev => prev ? ({
          ...prev,
          thumbnail_url: dataUrl
        }) : null);

        toast({
          title: "Thumbnail atualizada",
          description: "A capa foi definida com sucesso (visualização local).",
          className: "bg-green-500 text-white border-none"
        });
      } catch (error) {
        console.error("Erro ao gerar snapshot:", error);
        toast({
            title: "Erro de segurança",
            description: "Não foi possível capturar a imagem (CORS Policy).",
            variant: "destructive"
        });
      }
    }
  };

  if (isLoading) {
    return <div className="h-full w-full bg-zinc-950 flex items-center justify-center">
      <Loader2 className="animate-spin text-white w-8 h-8"/>
    </div>;
  }

  return (
    <div className="h-full w-full relative bg-zinc-950 overflow-hidden">
      
      {/* 1. MAPA DE FUNDO */}
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

      {/* 2. SIDEBAR FLUTUANTE */}
      <div className="absolute top-4 left-4 z-10">
        <Sheet>
          <SheetTrigger asChild>
            <Button size="icon" className="h-10 w-10 rounded-xl shadow-lg bg-black/40 backdrop-blur-md hover:bg-black/60 border border-white/10 text-white transition-all duration-300">
              <List className="h-5 w-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className={`p-0 w-[320px] sm:w-[380px] ${glassSheetClasses}`}>
             <div className="h-full pt-12 px-1"> 
                <CameraSideList 
                  cameras={cameras} 
                  selectedId={selectedCamera?.id} 
                  onSelect={(cam) => {
                      const fullCam = cameras.find(c => c.id === cam.id);
                      if (fullCam) handleCameraSelect(fullCam);
                  }} 
                />
             </div>
          </SheetContent>
        </Sheet>
      </div>

      {/* 3. CONTAINER PRINCIPAL (Player + Timeline) */}
      <div 
        className={cn(
          "absolute bottom-0 left-0 right-0 z-20 transition-transform duration-500 ease-in-out bg-black/90 backdrop-blur-xl shadow-2xl border-t border-white/10 flex flex-col",
          selectedCamera ? "translate-y-0" : "translate-y-full",
          isPlayerExpanded ? "h-[90%]" : "h-[50%]",
          isTimelineExpanded ? "z-50" : "z-20"
        )}
      >
        {selectedCamera && (
          <>
            {/* Header do Player */}
            <div className="flex items-center justify-between px-4 py-3 bg-white/5 border-b border-white/5 shrink-0">
              <div className="flex items-center gap-3">
                <div className={`w-2.5 h-2.5 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.5)] ${selectedCamera.status === 'online' ? 'bg-green-500 shadow-green-500/50' : 'bg-red-500 shadow-red-500/50'} animate-pulse`} />
                <div>
                   <h3 className="font-semibold text-white text-sm leading-none">{selectedCamera.name}</h3>
                   <p className="text-[10px] text-white/50 mt-0.5">{selectedCamera.location}</p>
                </div>
              </div>
              
              <div className="flex items-center gap-1">
                <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-8 w-8 text-white/50 hover:text-white hover:bg-white/10 rounded-full"
                    onClick={() => setIsPlayerExpanded(!isPlayerExpanded)}
                >
                  {isPlayerExpanded ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
                </Button>
                <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-8 w-8 text-white/50 hover:text-red-400 hover:bg-red-500/10 rounded-full"
                    onClick={handleClosePlayer}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Área do Vídeo */}
            <div className="flex-1 relative bg-black overflow-hidden flex items-center justify-center group">
               <VideoPlayer
                  url={selectedCamera.stream_url_frontend}
                  poster={selectedCamera.thumbnail_url}
                  className="w-full h-full"
                  videoRefProp={videoRef} // Passando a referência para o player
                />

                {/* Botão de Snapshot (Toast Action) */}
                <Button 
                  onClick={handleSnapshot}
                  className="absolute bottom-6 right-6 z-50 bg-zinc-900/90 hover:bg-zinc-800 text-white gap-2 border border-white/10 shadow-lg backdrop-blur-sm transition-opacity duration-300 opacity-0 group-hover:opacity-100"
                >
                  <Camera className="w-4 h-4" />
                  <span>Atualizar thumb</span>
                </Button>
            </div>

            {/* TIMELINE */}
            <div 
              className={cn(
                "transition-all duration-500 ease-in-out bg-black/95 border-t border-white/10",
                isTimelineExpanded 
                  ? "fixed inset-0 z-[60] flex flex-col items-center justify-center" 
                  : "relative shrink-0 h-24 z-30"
              )}
            >
               <Timeline
                  currentTime={new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                  events={mockTimelineEvents}
                  className="border-0 bg-transparent w-full h-full"
                  isExpanded={isTimelineExpanded}
                  onToggleExpand={() => setIsTimelineExpanded(!isTimelineExpanded)}
               />
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default LiveCameras;