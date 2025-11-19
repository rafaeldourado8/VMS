import { useEffect, useRef } from 'react';
import * as WebRTCPlayerPkg from '@eyevinn/webrtc-player';

interface WebRTCPlayerProps {
  whepURL: string;
}

const WebRTCPlayer = ({ whepURL }: WebRTCPlayerProps) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const playerRef = useRef<any | null>(null);

  const resolveLibPlayer = () => {
    const pkgAny = WebRTCPlayerPkg as any;
    return pkgAny.WebRTCPlayer ?? pkgAny.default ?? pkgAny;
  };

  useEffect(() => {
    const LibPlayer = resolveLibPlayer();

    if (!videoRef.current) return;

    if (playerRef.current) {
      try {
        playerRef.current.stop?.();
        playerRef.current.disconnect?.();
      } catch (e) {
        console.warn('Erro ao desconectar player anterior:', e);
      }
      playerRef.current = null;
    }

    if (!whepURL) {
      console.warn('WebRTCPlayer: nenhuma URL fornecida.');
      return;
    }

    let urlObj: URL | null = null;
    try {
      try {
        urlObj = new URL(whepURL);
      } catch (err) {
        urlObj = new URL(whepURL, window.location.origin);
      }
    } catch (err) {
      console.error('WebRTCPlayer: whepURL inválida:', whepURL, err);
      return;
    }

    if (typeof LibPlayer !== 'function') {
      console.error('WebRTCPlayer library export não é uma função:', LibPlayer);
      return;
    }

    try {
      playerRef.current = new LibPlayer({
        video: videoRef.current,
        type: 'whep',
      });
    } catch (err) {
      console.error('Falha ao instanciar o player WebRTC:', err);
      playerRef.current = null;
      return;
    }

    const start = async () => {
      try {
        if (typeof playerRef.current.load === 'function') {
          await playerRef.current.load(urlObj!);
        } else if (typeof playerRef.current.connect === 'function') {
          await playerRef.current.connect(urlObj!.toString());
        } else {
          console.warn('Player instance não possui método load nem connect:', playerRef.current);
        }
      } catch (err) {
        console.error('Erro ao carregar/conectar stream WHEP:', err);
      }
    };

    start();

    return () => {
      try {
        playerRef.current?.stop?.();
        playerRef.current?.disconnect?.();
      } catch (e) {}
      playerRef.current = null;
    };
  }, [whepURL]);

  return (
    <video
      ref={videoRef}
      autoPlay
      muted
      controls
      playsInline
      className="w-full h-full object-contain"
    />
  );
};

export default WebRTCPlayer;