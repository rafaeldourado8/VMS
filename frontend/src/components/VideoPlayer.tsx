import React, { useRef, useEffect } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useHlsPlayer } from '@/hooks/useHlsPlayer';
import { Skeleton } from '@/components/ui/skeleton';

interface VideoPlayerProps {
  url: string;
  poster?: string | null;
  className?: string;
  // Usamos ref para passar dados para cima sem re-renderizar
  onTimeUpdate?: (currentTime: number, duration: number) => void;
  videoRefProp?: React.RefObject<HTMLVideoElement>; 
}

const VideoPlayer = React.memo(({ 
  url, 
  poster, 
  className, 
  onTimeUpdate,
  videoRefProp 
}: VideoPlayerProps) => {
  const internalRef = useRef<HTMLVideoElement>(null);
  const videoRef = (videoRefProp || internalRef) as React.MutableRefObject<HTMLVideoElement>;
  
  const { isLoading, error } = useHlsPlayer({ url, videoRef });

  useEffect(() => {
    let animationFrameId: number;

    const loop = () => {
      if (videoRef.current && onTimeUpdate) {
        onTimeUpdate(videoRef.current.currentTime, videoRef.current.duration || 0);
      }
      animationFrameId = requestAnimationFrame(loop);
    };

    if (!isLoading) loop();

    return () => cancelAnimationFrame(animationFrameId);
  }, [isLoading]); // Dependências mínimas

  return (
    <div className={cn("relative w-full h-full bg-black overflow-hidden group rounded-t-lg", className)}>
      <video
        ref={videoRef}
        poster={poster || undefined}
        className={cn("w-full h-full object-contain", isLoading ? "opacity-0" : "opacity-100")}
        playsInline
        crossOrigin="anonymous"
      />

      {/* Loading State */}
      {isLoading && !error && (
        <div className="absolute inset-0 z-20">
           <Skeleton className="w-full h-full bg-zinc-800" />
           <div className="absolute inset-0 flex flex-col items-center justify-center">
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
              <span className="text-white/80 font-medium text-sm tracking-widest uppercase">Carregando Stream...</span>
           </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-zinc-900 z-30">
          <AlertCircle className="w-12 h-12 text-red-500 mb-2 opacity-80" />
          <span className="text-white text-sm font-medium">{error}</span>
          <button onClick={() => window.location.reload()} className="mt-4 text-xs text-blue-400 hover:underline">Tentar reconectar</button>
        </div>
      )}
    </div>
  );
});

export default VideoPlayer;