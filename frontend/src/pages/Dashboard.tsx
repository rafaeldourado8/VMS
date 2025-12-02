// VMS/frontend/src/pages/Dashboard.tsx
import { useState, useRef, useCallback, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/axios';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/use-toast';

// Componentes UI
import { Button } from '@/components/ui/button';
import { X, Camera } from 'lucide-react';

// Componentes Isolados (Novos)
import MapViewer, { Camera as CameraType } from '@/components/MapViewer';
import VideoPlayer from '@/components/VideoPlayer';
import Timeline from '@/components/Timeline';
import { FullscreenWrapper } from '@/components/FullscreenWrapper';
import { CameraStatusBadge } from '@/components/CameraStatusBadge';

const Dashboard = () => {
  const [activeCamera, setActiveCamera] = useState<CameraType | null>(null);
  const [isUiHidden, setIsUiHidden] = useState(false); // Controlado pelo FullscreenWrapper
  const [streamStatus, setStreamStatus] = useState<string>('offline');
  
  // Estado do vídeo controlado pelo Dashboard para sincronizar com Timeline
  const [videoState, setVideoState] = useState({ currentTime: 0, duration: 0, isPlaying: false });
  const videoElementRef = useRef<HTMLVideoElement>(null);
  const { toast } = useToast();

  // Busca Câmeras
  const { data: cameras = [], isLoading } = useQuery({
    queryKey: ['cameras'],
    queryFn: async () => {
      const response = await api.get('/cameras/');
      const list = response.data.results || response.data || [];
      return list.map((c: any) => ({
          ...c,
          stream_url: c.stream_url_frontend || c.stream_url
      }));
    },
    staleTime: 60000,
  });

  // Efeito para definir status inicial correto
  useEffect(() => {
    if (activeCamera) {
        // Se a API diz que tá online, confiamos nela inicialmente.
        // O player mudará para 'offline' apenas se der erro de reprodução.
        setStreamStatus(activeCamera.status);
    }
  }, [activeCamera]);

  // Handlers do Player
  const handleTimeUpdate = useCallback((currentTime: number, duration: number) => {
    setVideoState(prev => ({ ...prev, currentTime, duration: duration || prev.duration }));
  }, []);

  const handlePlayerPlaying = useCallback(() => {
      setStreamStatus('online');
      setVideoState(prev => ({ ...prev, isPlaying: true }));
  }, []);

  const handlePlayerError = useCallback(() => {
      setStreamStatus('offline');
      setVideoState(prev => ({ ...prev, isPlaying: false }));
  }, []);

  // Handlers da Timeline
  const handleSeek = (time: number) => {
    if (videoElementRef.current) {
        videoElementRef.current.currentTime = time;
        setVideoState(prev => ({ ...prev, currentTime: time }));
    }
  };

  const togglePlay = () => {
    if (videoElementRef.current) {
        if (videoElementRef.current.paused) {
            videoElementRef.current.play();
            setVideoState(prev => ({ ...prev, isPlaying: true }));
        } else {
            videoElementRef.current.pause();
            setVideoState(prev => ({ ...prev, isPlaying: false }));
        }
    }
  };

  const handleSaveClip = (start: number, end: number) => {
      console.log(`Salvando clipe: ${start.toFixed(2)}s a ${end.toFixed(2)}s`);
      toast({
          title: "Clipe Solicitado",
          description: `Processando recorte de ${start.toFixed(0)}s até ${end.toFixed(0)}s`,
      });
  };

  if (isLoading) return <div className="w-full h-full flex items-center justify-center bg-zinc-950 text-white">Carregando sistema...</div>;

  return (
    <div className="w-full h-full relative overflow-hidden">
        {/* Mapa de Fundo */}
        <MapViewer 
            cameras={cameras} 
            height="100%" 
            onCameraDoubleClick={setActiveCamera} 
        />

        {/* Modal da Câmera Ativa */}
        {activeCamera && (
            <div className={cn(
                "fixed inset-0 z-50 flex items-center justify-center transition-all duration-300",
                // Se UI estiver escondida (Fullscreen), fundo preto total. Senão, blur.
                isUiHidden ? "bg-black" : "bg-black/80 backdrop-blur-sm p-4"
            )}>
                <div className={cn(
                    "flex flex-col bg-white overflow-hidden shadow-2xl transition-all duration-300 border border-white/10",
                    isUiHidden 
                        ? "w-full h-full rounded-none" 
                        : "w-full h-full md:h-auto md:w-full md:max-w-5xl md:rounded-xl md:max-h-[90vh]"
                )}>
                    
                    {/* Header (Esconde no Fullscreen) */}
                    {!isUiHidden && (
                        <div className="flex items-center justify-between px-4 py-3 bg-white border-b shrink-0 h-14">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-slate-100 rounded-lg text-slate-600">
                                    <Camera className="w-5 h-5" />
                                </div>
                                <div>
                                    <h2 className="font-bold text-slate-800 text-sm">{activeCamera.name}</h2>
                                    <div className="flex items-center gap-2">
                                        <p className="text-xs text-slate-500 uppercase">{activeCamera.location}</p>
                                        <div className="h-1 w-1 bg-slate-300 rounded-full" />
                                        <CameraStatusBadge status={streamStatus} />
                                    </div>
                                </div>
                            </div>
                            <Button variant="ghost" size="icon" onClick={() => setActiveCamera(null)} className="hover:bg-red-50 hover:text-red-600">
                                <X className="w-5 h-5" />
                            </Button>
                        </div>
                    )}

                    {/* Conteúdo Principal */}
                    <div className={cn("flex flex-col bg-black relative", isUiHidden ? "flex-1" : "")}>
                        
                        {/* Wrapper de Fullscreen Isolado */}
                        <FullscreenWrapper 
                            className={cn("w-full relative flex items-center justify-center bg-black", isUiHidden ? "h-full" : "aspect-video")}
                            onFullscreenChange={setIsUiHidden}
                        >
                            <VideoPlayer 
                                url={activeCamera.stream_url || ""} 
                                poster={activeCamera.thumbnail_url} 
                                videoRefProp={videoElementRef}
                                onTimeUpdate={handleTimeUpdate}
                                onPlaying={handlePlayerPlaying}
                                onError={handlePlayerError}
                                className="w-full h-full"
                            />
                        </FullscreenWrapper>

                        {/* Timeline (Esconde no Fullscreen) */}
                        {!isUiHidden && (
                            <div className="shrink-0 bg-white border-t z-20">
                                <Timeline 
                                    currentTime={videoState.currentTime}
                                    duration={videoState.duration}
                                    isPlaying={videoState.isPlaying}
                                    onSeek={handleSeek}
                                    onTogglePlay={togglePlay}
                                    onSaveClip={handleSaveClip}
                                />
                            </div>
                        )}
                    </div>
                </div>
            </div>
        )}
    </div>
  );
};

export default Dashboard;