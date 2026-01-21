import { useEffect, useState } from 'react';
import { Car, Clock, Camera, AlertCircle } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/ui';
// [CORREÇÃO 1] Usar o detectionService que já tem autenticação configurada
import { detectionService } from '@/services/api'; 
// Usar a tipagem centralizada para evitar conflitos
import type { Detection } from '@/types';

export function LiveDetections() {
  const [detections, setDetections] = useState<Detection[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDetections();
    const interval = setInterval(fetchDetections, 3000); // Polling 3s
    return () => clearInterval(interval);
  }, []);

  const fetchDetections = async () => {
    try {
      // [CORREÇÃO 2] Chamada via serviço autenticado
      const response = await detectionService.list({
        page: 1,
        // Se o backend suportar ordering nos params diretos:
        // ordering: '-timestamp' 
      });

      // Normaliza a resposta (suporta PaginatedResponse ou Array direto)
      const rawData = Array.isArray(response) ? response : response.results;
      
      // [DEBUG] Verifique isso no Console do Navegador (F12)
      console.log("📡 Dados recebidos do Backend:", rawData);

      if (!rawData) {
        setDetections([]);
        return;
      }

      // [CORREÇÃO 3] Filtragem mais robusta (converte para Number)
      const filtered = rawData.filter((d: any) => {
        const conf = Number(d.confidence);
        // Aceita se tiver confiança > 50% OU se não tiver campo de confiança (para não esconder erros)
        return isNaN(conf) || conf >= 0.5;
      });

      setDetections(filtered);
      setError(null);
    } catch (err) {
      console.error('❌ Erro ao buscar detecções:', err);
      // Exibe erro na tela para facilitar diagnóstico
      setError('Falha ao carregar dados. Verifique o console.');
    } finally {
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
            <div className={`w-2 h-2 rounded-full ${!isLoading && !error ? 'bg-emerald-500' : 'bg-yellow-500'} animate-pulse`} />
            <span className="text-xs text-muted-foreground">
              {error ? 'Erro' : (!isLoading ? 'Ao vivo' : 'Conectando...')}
            </span>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="px-2">
        {error && (
            <div className="p-3 mb-2 text-xs text-red-500 bg-red-500/10 rounded border border-red-500/20 flex gap-2 items-center">
                <AlertCircle className="w-4 h-4" />
                {error}
            </div>
        )}

        {detections.length === 0 && !isLoading ? (
          <div className="text-center py-8 text-muted-foreground/50">
            <p className="text-sm">Nenhuma detecção encontrada</p>
            <p className="text-xs mt-1">(Aguardando dados da IA...)</p>
          </div>
        ) : (
          <div className="space-y-3">
            {detections.map((det) => (
              <div key={det.id} className="flex items-start gap-3 p-3 rounded-lg border bg-card/50 hover:bg-accent/10 transition-colors animate-in fade-in slide-in-from-top-2 duration-300">
                
                {/* Imagem da Placa */}
                {det.image_url ? (
                  <div className="w-20 h-12 bg-black/20 rounded overflow-hidden flex-shrink-0 border border-white/10 group relative">
                    <img 
                      src={det.image_url}
                      className="w-full h-full object-cover transition-transform group-hover:scale-110" 
                      alt={`Placa ${det.plate}`}
                      onError={(e) => { e.currentTarget.style.display = 'none'; }}
                    />
                  </div>
                ) : (
                  <div className="w-20 h-12 bg-muted/20 rounded flex items-center justify-center text-muted-foreground text-xs">
                    Sem img
                  </div>
                )}

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-mono font-bold tracking-wider text-green-400">
                      {det.plate || "DESCONHECIDO"}
                    </span>
                    {det.confidence !== null && (
                        <Badge variant="outline" className="text-[10px] h-5">
                        {(Number(det.confidence) * 100).toFixed(0)}%
                        </Badge>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Camera className="w-3 h-3" /> 
                      {/* Tenta usar camera_name se existir, senão usa ID */}
                      {(det as any).camera_name || `Cam ${det.camera_id}`}
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