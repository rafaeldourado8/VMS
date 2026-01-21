import { useEffect, useState } from 'react';
import { Car, Clock, Camera } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/ui';
import { api } from '@/infrastructure/api/client';

interface Detection {
  id: string;
  camera_id: number;
  plate: string;
  confidence: number;
  timestamp: string;
  image_url?: string;
}

export function LiveDetections() {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Busca inicial
    fetchDetections();
    
    // Polling a cada 3 segundos
    const interval = setInterval(fetchDetections, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchDetections = async () => {
    try {
      const response = await api.get('/detections/', {
        params: { limit: 10, ordering: '-timestamp' }
      });
      const data = response.data.results || response.data;
      // Filtra apenas detecções com confiança >= 70%
      setDetections(data.filter((d: Detection) => d.confidence >= 0.7));
      setIsLoading(false);
    } catch (error) {
      console.error('Erro ao buscar detecções:', error);
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full h-full border-none shadow-none">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-medium flex items-center gap-2">
            <Car className="w-4 h-4 text-primary" />
            Detecções Recentes
          </CardTitle>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${!isLoading ? 'bg-emerald-500' : 'bg-yellow-500'} animate-pulse`} />
            <span className="text-xs text-muted-foreground">
              {!isLoading ? 'Atualizado' : 'Carregando...'}
            </span>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="px-2">
        {detections.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground/50">
            <p className="text-sm">Nenhuma detecção encontrada</p>
          </div>
        ) : (
          <div className="space-y-3">
            {detections.map((det) => (
              <div key={det.id} className="flex items-start gap-3 p-3 rounded-lg border bg-card/50 hover:bg-accent/10 transition-colors">
                
                {/* Imagem da Placa */}
                {det.image_url && (
                  <div className="w-20 h-12 bg-black/20 rounded overflow-hidden flex-shrink-0 border border-white/10">
                    <img 
                      src={det.image_url}
                      className="w-full h-full object-cover" 
                      alt="Placa"
                      onError={(e) => { e.currentTarget.style.display = 'none'; }}
                    />
                  </div>
                )}

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-mono font-bold tracking-wider text-green-400">
                      {det.plate}
                    </span>
                    <Badge variant="outline" className="text-[10px] h-5">
                      {(det.confidence * 100).toFixed(0)}%
                    </Badge>
                  </div>
                  
                  <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Camera className="w-3 h-3" /> Cam {det.camera_id}
                    </span>
                    <span className="flex items-center gap-1 ml-auto">
                      <Clock className="w-3 h-3" />
                      {new Date(det.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}