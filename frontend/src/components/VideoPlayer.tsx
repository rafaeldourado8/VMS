import { useEffect, useRef, useState } from 'react';
import Hls from 'hls.js';
import { AlertCircle, Loader2 } from 'lucide-react';

interface VideoPlayerProps {
  url: string;
  poster?: string | null;
}

const VideoPlayer = ({ url, poster }: VideoPlayerProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let hls: Hls | null = null;

    const initPlayer = () => {
      if (!url) return;
      
      // --- LOG PARA DEPURAÇÃO ---
      console.log('[VideoPlayer] Tentando carregar URL:', url);
      
      setIsLoading(true);
      setError(null);

      const video = videoRef.current;
      if (!video) return;

      // 1. Tenta suporte nativo (Safari/iOS)
      if (video.canPlayType('application/vnd.apple.mpegurl')) {
        console.log('[VideoPlayer] Usando suporte nativo HLS (Safari)');
        video.src = url;
        video.play()
          .then(() => setIsLoading(false))
          .catch((e) => {
            console.warn('[VideoPlayer] Autoplay nativo bloqueado:', e);
            // Não removemos isLoading aqui pois o evento 'playing' ou 'loadeddata' deve tratar
          });
        
        // Listeners nativos para atualizar estado
        video.onloadeddata = () => setIsLoading(false);
        video.onerror = () => {
            console.error('[VideoPlayer] Erro nativo:', video.error);
            setError('Erro ao carregar vídeo (Nativo).');
            setIsLoading(false);
        };
      }
      // 2. Tenta Hls.js (Chrome, Firefox, Edge)
      else if (Hls.isSupported()) {
        console.log('[VideoPlayer] Inicializando Hls.js');
        hls = new Hls({
          debug: false, // Mude para true se precisar ver logs detalhados do Hls.js
          enableWorker: true,
          lowLatencyMode: true,
        });

        hls.loadSource(url);
        hls.attachMedia(video);

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          console.log('[VideoPlayer] Manifesto carregado, iniciando reprodução...');
          setIsLoading(false);
          video.play().catch((e) => console.warn('[VideoPlayer] Autoplay Hls.js bloqueado:', e));
        });

        hls.on(Hls.Events.ERROR, (_event, data) => {
          if (data.fatal) {
            console.error('[VideoPlayer] Erro fatal Hls.js:', data);
            switch (data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
                console.error("[VideoPlayer] Erro de rede. URL inacessível?");
                hls?.startLoad(); // Tenta recuperar
                break;
              case Hls.ErrorTypes.MEDIA_ERROR:
                console.error("[VideoPlayer] Erro de mídia. Tentando recuperar...");
                hls?.recoverMediaError();
                break;
              default:
                setError("Erro fatal na reprodução.");
                setIsLoading(false);
                hls?.destroy();
                break;
            }
          }
        });
      } else {
        console.error('[VideoPlayer] HLS não suportado neste navegador.');
        setError('Seu navegador não suporta reprodução de vídeo HLS.');
        setIsLoading(false);
      }
    };

    initPlayer();

    return () => {
      if (hls) {
        hls.destroy();
      }
      if (videoRef.current) {
        // Limpa a fonte para parar o download em background
        videoRef.current.removeAttribute('src');
        videoRef.current.load();
      }
    };
  }, [url]);

  return (
    <div className="relative w-full h-full bg-black rounded-lg overflow-hidden group">
      {isLoading && !error && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-10">
          <Loader2 className="w-8 h-8 text-white animate-spin" />
          <span className="ml-2 text-white text-sm">Carregando Stream...</span>
        </div>
      )}
      
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/80 z-20">
          <AlertCircle className="w-6 h-6 text-red-500 mr-2" />
          <span className="text-red-400 text-sm">{error}</span>
        </div>
      )}

      <video
        ref={videoRef}
        poster={poster || undefined}
        className="w-full h-full object-contain"
        controls
        muted // Importante para autoplay funcionar na maioria dos browsers
        autoPlay
        playsInline
        crossOrigin="anonymous" // Ajuda com CORS se o MediaMTX estiver em outra porta
      />
    </div>
  );
};

export default VideoPlayer;