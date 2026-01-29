import { useEffect, useRef, useState } from 'react';
import { Play, Loader2 } from 'lucide-react';

interface WebRTCPlayerProps {
  cameraId: number;
  mediaMtxUrl?: string;
  className?: string;
}

export default function WebRTCPlayer({ 
  cameraId, 
  mediaMtxUrl = 'http://localhost:8889',
  className = '' 
}: WebRTCPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const startStream = async () => {
    if (!videoRef.current) return;
    
    setIsLoading(true);
    setError(null);

    try {
      const pc = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
      });

      pc.ontrack = (event) => {
        if (videoRef.current && event.streams[0]) {
          videoRef.current.srcObject = event.streams[0];
          setIsPlaying(true);
        }
      };

      pc.oniceconnectionstatechange = () => {
        if (pc.iceConnectionState === 'failed' || pc.iceConnectionState === 'disconnected') {
          setError('Conexão perdida');
          setIsPlaying(false);
        }
      };

      pc.addTransceiver('video', { direction: 'recvonly' });
      pc.addTransceiver('audio', { direction: 'recvonly' });

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const whepUrl = `${mediaMtxUrl}/cam_${cameraId}_ai/whep`;
      const res = await fetch(whepUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/sdp' },
        body: offer.sdp
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: Stream não disponível`);
      }

      const answer = await res.text();
      await pc.setRemoteDescription({ 
        type: 'answer', 
        sdp: answer 
      });

      pcRef.current = pc;
    } catch (err) {
      console.error('WebRTC error:', err);
      setError(err instanceof Error ? err.message : 'Erro ao conectar');
      setIsPlaying(false);
    } finally {
      setIsLoading(false);
    }
  };

  const stopStream = () => {
    if (pcRef.current) {
      pcRef.current.close();
      pcRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsPlaying(false);
  };

  useEffect(() => {
    return () => stopStream();
  }, [cameraId]);

  return (
    <div className={`relative bg-black rounded-lg overflow-hidden ${className}`}>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-full object-contain"
      />
      
      {!isPlaying && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 bg-black/50">
          {error ? (
            <>
              <div className="text-red-400 text-center px-4">
                <div className="font-semibold mb-1">Erro</div>
                <div className="text-sm">{error}</div>
              </div>
              <button
                onClick={startStream}
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg flex items-center gap-2"
              >
                {isLoading ? <Loader2 className="animate-spin" size={20} /> : <Play size={20} />}
                Tentar Novamente
              </button>
            </>
          ) : (
            <button
              onClick={startStream}
              disabled={isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg flex items-center gap-2"
            >
              {isLoading ? <Loader2 className="animate-spin" size={20} /> : <Play size={20} />}
              {isLoading ? 'Conectando...' : 'Iniciar Stream IA'}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
