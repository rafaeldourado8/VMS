import { useEffect, useRef, useState, MutableRefObject } from 'react';
import type Hls from 'hls.js';

interface UseHlsPlayerProps {
  url: string;
  videoRef: MutableRefObject<HTMLVideoElement | null>;
  autoPlay?: boolean;
}

export const useHlsPlayer = ({ url, videoRef, autoPlay = true }: UseHlsPlayerProps) => {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  // Removemos estados que mudam muito rápido daqui para evitar re-renders no hook
  const hlsRef = useRef<Hls | null>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !url) return;

    setIsLoading(true);
    setError(null);

    const cleanup = () => {
      if (hlsRef.current) {
        hlsRef.current.stopLoad(); // Para o download imediatamente
        hlsRef.current.detachMedia();
        hlsRef.current.destroy();
        hlsRef.current = null;
      }
    };

    const initHls = async () => {
      cleanup();

      // Lazy load HLS.js
      const HlsModule = await import('hls.js');
      const Hls = HlsModule.default;

      if (Hls.isSupported()) {
        const hls = new Hls({
          debug: false,
          enableWorker: true,
          lowLatencyMode: true,
          // Ajuste para estabilidade:
          backBufferLength: 60,
          maxBufferLength: 30, // Aumentado para evitar travamento se a rede oscilar
          liveSyncDurationCount: 3, 
          // Recuperação agressiva de erros
          manifestLoadingTimeOut: 15000,
          manifestLoadingMaxRetry: 5,
        });

        hlsRef.current = hls;
        hls.loadSource(url);
        hls.attachMedia(video);

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          setIsLoading(false);
          if (autoPlay) {
            const playPromise = video.play();
            if (playPromise !== undefined) {
              playPromise.catch(() => {
                video.muted = true;
                video.play().catch(() => {});
              });
            }
          }
        });

        hls.on(Hls.Events.ERROR, (_event, data) => {
          if (data.fatal) {
            switch (data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
                hls.startLoad();
                break;
              case Hls.ErrorTypes.MEDIA_ERROR:
                hls.recoverMediaError();
                break;
              default:
                cleanup();
                setError("Erro de conexão com a câmera.");
                break;
            }
          }
        });
      } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = url;
        video.addEventListener('loadedmetadata', () => setIsLoading(false));
      }
    };

    initHls();

    return () => {
      cleanup();
      if (video) {
        video.removeAttribute('src');
        video.load();
      }
    };
  }, [url]); // Removido videoRef e autoPlay das deps para evitar recriação desnecessária

  return { isLoading, error };
};