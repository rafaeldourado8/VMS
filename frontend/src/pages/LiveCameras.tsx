import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import api from '@/lib/axios';
import { useToast } from '@/hooks/use-toast';
import WebRTCPlayer from '@/components/WebRTCPlayer';

interface Camera {
  id: number;
  name: string;
  thumbnail_url?: string | null;
  webrtc_url: string;
}

const LiveCameras = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const response = await api.get('/cameras/');
        const raw = response.data;
        const list = Array.isArray(raw) ? raw : (Array.isArray(raw?.results) ? raw.results : []);

        const normalized: Camera[] = list.map((c: any) => ({
          id: c.id,
          name: c.name,
          thumbnail_url: c.thumbnail_url ?? c.thumbnail ?? null,
          webrtc_url: c.webrtc_url
            ? (c.webrtc_url.startsWith('/')
                ? `${window.location.origin}${c.webrtc_url}`
                : c.webrtc_url)
            : '',
        }));

        setCameras(normalized);
        if (normalized.length > 0) {
          setSelectedCamera(normalized[0]);
        } else {
          setSelectedCamera(null);
        }
      } catch (error) {
        console.error('Erro ao buscar câmeras:', error);
        toast({
          title: 'Erro ao carregar câmeras',
          variant: 'destructive',
        });
      }
    };

    fetchCameras();
  }, [toast]);

  return (
    <div className="flex h-screen">
      <div className="flex-1 p-8">
        <div className="h-full flex flex-col">
          <h1 className="text-3xl font-bold text-foreground mb-6">Câmeras ao Vivo</h1>
          <Card className="flex-1 bg-black flex items-center justify-center">
            {selectedCamera ? (
              <WebRTCPlayer whepURL={selectedCamera.webrtc_url} />
            ) : (
              <div className="text-center text-white space-y-4">
                <h2 className="text-2xl font-semibold">Player de Vídeo</h2>
                <p className="text-muted-foreground">Selecione uma câmera na lista</p>
              </div>
            )}
          </Card>
        </div>
      </div>

      <div className="w-80 border-l bg-card">
        <div className="p-4 border-b">
          <h3 className="font-semibold">Lista de Câmeras</h3>
          <p className="text-sm text-muted-foreground">{cameras.length} disponíveis</p>
        </div>
        <ScrollArea className="h-[calc(100vh-80px)]">
          <div className="p-4 space-y-2">
            {Array.isArray(cameras) && cameras.map((camera) => (
              <button
                key={camera.id}
                onClick={() => setSelectedCamera(camera)}
                className={`w-full p-3 rounded-lg border transition-colors text-left ${
                  selectedCamera?.id === camera.id
                    ? 'bg-primary/10 border-primary'
                    : 'bg-card hover:bg-muted border-border'
                }`}
              >
                {camera.thumbnail_url ? (
                  <img
                    src={camera.thumbnail_url}
                    alt={camera.name}
                    className="w-full h-32 object-cover rounded mb-2"
                  />
                ) : (
                  <div className="w-full h-32 bg-muted rounded mb-2 flex items-center justify-center">
                    <span className="text-xs text-muted-foreground">Sem miniatura</span>
                  </div>
                )}
                <p className="font-medium text-sm">{camera.name}</p>
              </button>
            ))}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
};

export default LiveCameras;