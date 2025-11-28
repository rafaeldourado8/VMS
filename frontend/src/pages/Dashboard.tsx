import { useState, useRef, useCallback, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/axios';
import MapViewer, { Camera as CameraType } from '@/components/MapViewer';
import { X, Maximize, Minimize, Camera } from 'lucide-react';
import VideoPlayer from '@/components/VideoPlayer';
import Timeline from '@/components/Timeline';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const Dashboard = () => {
  const [activeCamera, setActiveCamera] = useState<CameraType | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  
  // Estado do Vídeo e STATUS REAL
  const [videoState, setVideoState] = useState({ currentTime: 0, duration: 0, isPlaying: false });
  const [streamStatus, setStreamStatus] = useState<'online' | 'offline' | 'loading'>('loading');
  const videoElementRef = useRef<HTMLVideoElement>(null);

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

  // Resetar status ao abrir nova câmera
  useEffect(() => {
    if (activeCamera) {
        // Assume 'loading' até o player confirmar ou dar erro
        setStreamStatus('loading');
    }
  }, [activeCamera]);

  // Callbacks do Player
  const handlePlayerPlaying = useCallback(() => setStreamStatus('online'), []);
  const handlePlayerError = useCallback(() => setStreamStatus('offline'), []);

  const handleTimeUpdate = useCallback((currentTime: number, duration: number) => {
    setVideoState(prev => {
        if (Math.abs(prev.currentTime - currentTime) < 0.5 && prev.duration === duration) return prev;
        return { ...prev, currentTime, duration: duration || prev.duration };
    });
  }, []);

  const handleSeek = (time: number) => {
    if (videoElementRef.current) {
        videoElementRef.current.currentTime = time;
        setVideoState(prev => ({ ...prev, currentTime: time }));
    }
  };

  const togglePlay = () => {
    if (videoElementRef.current) {
        videoElementRef.current.paused ? videoElementRef.current.play() : videoElementRef.current.pause();
        setVideoState(prev => ({ ...prev, isPlaying: !videoElementRef.current?.paused }));
    }
  };

  const handleDoubleClick = (cam: CameraType) => {
    setActiveCamera(cam);
    setIsFullscreen(false);
  };

  if (isLoading) return <div className="w-full h-full flex items-center justify-center bg-zinc-950 text-white">Carregando...</div>;

  return (
    <div className="w-full h-full relative overflow-hidden">
        <MapViewer 
            cameras={cameras} 
            height="100%" 
            onCameraDoubleClick={handleDoubleClick} 
        />

        {activeCamera && (
            <div className={cn(
                "fixed inset-0 z-50 flex items-center justify-center transition-all duration-300",
                // Mobile: Fundo preto. Desktop: Fundo com blur.
                isFullscreen ? "bg-black p-0" : "bg-black md:bg-black/80 md:backdrop-blur-sm md:p-4"
            )}>
                <div className={cn(
                    "flex flex-col bg-white overflow-hidden shadow-2xl transition-all duration-300 border border-white/10",
                    isFullscreen 
                        ? "w-full h-full rounded-none" // Fullscreen real
                        : "w-full h-full md:h-auto md:w-full md:max-w-4xl md:rounded-xl" // Mobile: Tela cheia simulada / Desktop: Modal compacto
                )}>
                    
                    {/* Header */}
                    <div className="flex items-center justify-between px-3 md:px-4 py-2 md:py-3 bg-white border-b shrink-0 z-20 h-12 md:h-14">
                        <div className="flex items-center gap-3">
                            <div className="p-1.5 bg-blue-50 rounded-lg text-blue-600 hidden sm:block">
                                <Camera className="w-5 h-5" />
                            </div>
                            <div>
                                <h2 className="font-bold text-slate-800 text-sm leading-tight truncate max-w-[200px]">{activeCamera.name}</h2>
                                <p className="text-[10px] md:text-xs text-slate-500 font-medium uppercase">{activeCamera.location}</p>
                            </div>
                        </div>
                        <div className="flex gap-1 md:gap-2">
                            <Button variant="ghost" size="icon" onClick={() => setIsFullscreen(!isFullscreen)} title="Alternar Tela" className="h-8 w-8 md:h-9 md:w-9">
                                {isFullscreen ? <Minimize className="w-4 h-4 md:w-5 md:h-5 text-slate-600" /> : <Maximize className="w-4 h-4 md:w-5 md:h-5 text-slate-600" />}
                            </Button>
                            <Button variant="ghost" size="icon" onClick={() => setActiveCamera(null)} className="hover:bg-red-50 hover:text-red-600 h-8 w-8 md:h-9 md:w-9">
                                <X className="w-5 h-5 md:w-6 md:h-6" />
                            </Button>
                        </div>
                    </div>

                    {/* Área de Conteúdo */}
                    <div className={cn(
                        "flex flex-col bg-gray-100 relative",
                        isFullscreen ? "flex-1 min-h-0" : "flex-1 md:h-auto" // No mobile (flex-1) ocupa tudo. No desktop auto ajusta.
                    )}>
                        
                        {/* Vídeo */}
                        <div className={cn(
                            "bg-black relative w-full flex items-center justify-center overflow-hidden",
                            // Mobile/Fullscreen: Ocupa o resto da tela verticalmente
                            // Desktop Modal: Força aspect-video (16:9)
                            (isFullscreen || window.innerWidth < 768) ? "flex-1 min-h-0" : "aspect-video"
                        )}>
                            <VideoPlayer 
                                url={activeCamera.stream_url || ""} 
                                poster={activeCamera.thumbnail_url} 
                                videoRefProp={videoElementRef}
                                onTimeUpdate={handleTimeUpdate}
                                onPlaying={handlePlayerPlaying} // Atualiza status para online
                                onError={handlePlayerError}     // Atualiza status para offline
                                className="w-full h-full"
                            />
                        </div>

                        {/* Timeline */}
                        <div className="shrink-0 bg-white border-t z-20">
                            <Timeline 
                                currentTime={videoState.currentTime}
                                duration={videoState.duration}
                                isPlaying={videoState.isPlaying}
                                status={streamStatus} // Passa o status real
                                onSeek={handleSeek}
                                onTogglePlay={togglePlay}
                            />
                        </div>
                    </div>
                </div>
            </div>
        )}
    </div>
  );
};

export default Dashboard;