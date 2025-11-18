import { useEffect, useRef } from 'react';
// Import robusto para lidar com diferentes interops ESM/CJS
import * as WebRTCPlayerPkg from '@eyevinn/webrtc-player';

interface WebRTCPlayerProps {
  whepURL: string;
}

const WebRTCPlayer = ({ whepURL }: WebRTCPlayerProps) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const playerRef = useRef<any | null>(null);

  // Resolve a exportação correta da biblioteca (tolerante a default/named)
  const resolveLibPlayer = () => {
    const pkgAny = WebRTCPlayerPkg as any;
    // prefer named export WebRTCPlayer, fallback para default, fallback para objeto inteiro
    return pkgAny.WebRTCPlayer ?? pkgAny.default ?? pkgAny;
  };

  useEffect(() => {
    const LibPlayer = resolveLibPlayer();

    // Debug: confira o que foi importado
    console.debug('Resolved WebRTC player lib ->', typeof LibPlayer, LibPlayer);

    if (!videoRef.current) return;

    // limpa player anterior se existir
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
      console.warn('WebRTCPlayer: nenhuma URL fornecida (whepURL vazia).');
      return;
    }

    let urlObj: URL | null = null;
    try {
      urlObj = new URL(whepURL);
    } catch (err) {
      console.error('WebRTCPlayer: whepURL inválida:', whepURL, err);
      return;
    }

    // Verifica se a lib exportada é construtora
    if (typeof LibPlayer !== 'function') {
      console.error('WebRTCPlayer library export não é uma função/construtor:', LibPlayer);
      return;
    }

    // Cria instância do player da lib (nome da opção 'type' pode variar: 'whep' / 'se.eyevinn.whpp' etc.)
    try {
      playerRef.current = new LibPlayer({
        video: videoRef.current,
        type: 'whep', // ajuste se seu backend usar outro adapter (ex: 'se.eyevinn.whpp')
        // iceServers: [{ urls: 'stun:stun.l.google.com:19302' }], // opcional
      });
    } catch (err) {
      console.error('Falha ao instanciar o player WebRTC:', err);
      playerRef.current = null;
      return;
    }

    const start = async () => {
      try {
        // API oficial usa load(new URL(...))
        if (typeof playerRef.current.load === 'function') {
          await playerRef.current.load(urlObj!);
        } else if (typeof playerRef.current.connect === 'function') {
          // fallback se usar connect()
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
      } catch (e) {
        // ignora
      }
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