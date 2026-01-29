import { useState, useEffect } from 'react';
import { Eye, Camera, Activity, AlertCircle, Play } from 'lucide-react';
import WebRTCPlayer from '@/components/cameras/WebRTCPlayer';
import { useCameraStore } from '@/store/cameraStore';
import { aiService, cameraService } from '@/services/api'; // Serviços reais
import type { Camera as CameraType } from '@/types';

export default function AIStreamPage() {
  const [selectedCameraId, setSelectedCameraId] = useState<number | null>(null);
  const [isActivating, setIsActivating] = useState(false);
  const [activationError, setActivationError] = useState<string | null>(null);
  
  // Estado local para garantir dados frescos, independente da store global
  const [camerasList, setCamerasList] = useState<CameraType[]>([]);

  // 1. Carregar câmeras reais do Backend
  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const data = await cameraService.list();
        setCamerasList(data);
      } catch (error) {
        console.error("Erro ao buscar câmeras:", error);
      }
    };
    fetchCameras();
  }, []);

  // 2. Função para ativar o Pipeline de IA (On-Demand)
  const handleCameraSelect = async (cameraId: number) => {
    if (selectedCameraId === cameraId) return;

    setSelectedCameraId(cameraId);
    setIsActivating(true);
    setActivationError(null);

    try {
      // Chama o backend para subir o processo do YOLO/FFmpeg
      // Isso cria o stream 'cam_{id}_ai' no MediaMTX
      await aiService.startProcessing(cameraId);
    } catch (error) {
      console.error("Falha ao iniciar IA:", error);
      setActivationError("O serviço de IA não pôde ser iniciado. Verifique se o backend está rodando.");
    } finally {
      setIsActivating(false);
    }
  };

  const selectedCamera = camerasList.find(c => c.id === selectedCameraId);

  return (
    <div className="p-6 space-y-6 h-[calc(100vh-4rem)]">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Eye className="text-blue-600" />
            Visualização IA (WebRTC)
          </h1>
          <p className="text-gray-600 flex items-center gap-2">
            Pipeline de baixa latência com detecção veicular.
            <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded border border-green-200">
              WebRTC Ativo
            </span>
          </p>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6 h-full">
        {/* Lista de Câmeras */}
        <div className="bg-white rounded-lg shadow p-4 h-fit max-h-full overflow-y-auto">
          <h2 className="font-semibold mb-4 flex items-center gap-2">
            <Camera size={18} />
            Câmeras Disponíveis
          </h2>
          <div className="space-y-2">
            {camerasList.length === 0 && (
              <div className="text-center py-8 text-gray-400 text-sm">
                Nenhuma câmera cadastrada.
              </div>
            )}

            {camerasList.map((cam) => (
              <button
                key={cam.id}
                onClick={() => handleCameraSelect(cam.id)}
                className={`w-full text-left px-3 py-3 rounded-lg transition border ${
                  selectedCameraId === cam.id
                    ? 'bg-blue-50 border-blue-200 ring-1 ring-blue-300'
                    : 'bg-gray-50 border-transparent hover:bg-gray-100'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className={`font-medium ${selectedCameraId === cam.id ? 'text-blue-700' : 'text-gray-900'}`}>
                    {cam.name}
                  </span>
                  {selectedCameraId === cam.id && isActivating && (
                    <Activity size={14} className="animate-spin text-blue-600" />
                  )}
                </div>
                <div className="text-xs text-gray-500 truncate">
                  {cam.rtsp_url ? 'RTSP Configurado' : 'Sem URL'}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Player Area */}
        <div className="col-span-3 flex flex-col">
          <div className="bg-white rounded-lg shadow p-4 flex-1 flex flex-col min-h-[500px]">
            {selectedCameraId ? (
              <>
                <div className="mb-4 flex justify-between items-start">
                  <div>
                    <h2 className="text-xl font-semibold flex items-center gap-2">
                      {selectedCamera?.name}
                      {isActivating && <span className="text-sm font-normal text-blue-600 animate-pulse">(Iniciando Pipeline...)</span>}
                    </h2>
                    <p className="text-sm text-gray-500 font-mono mt-1">
                      Stream: <span className="bg-gray-100 px-1 rounded text-gray-700">cam_{selectedCameraId}_ai</span>
                    </p>
                  </div>
                </div>

                {activationError ? (
                   <div className="flex-1 flex flex-col items-center justify-center bg-red-50 rounded-lg text-red-600 p-8 text-center border border-red-100">
                     <AlertCircle size={48} className="mb-4" />
                     <h3 className="text-lg font-bold">Erro de Conexão</h3>
                     <p>{activationError}</p>
                     <button 
                       onClick={() => handleCameraSelect(selectedCameraId!)}
                       className="mt-4 px-4 py-2 bg-white border border-red-200 hover:bg-red-50 rounded-md font-medium transition shadow-sm"
                     >
                       Tentar Novamente
                     </button>
                   </div>
                ) : (
                  <div className="relative flex-1 bg-black rounded-lg overflow-hidden flex flex-col">
                     {/* IMPORTANTE: Usamos key={selectedCameraId} para forçar o React 
                        a desmontar e remontar o player quando trocamos de câmera.
                     */}
                     <WebRTCPlayer 
                       key={selectedCameraId}
                       cameraId={selectedCameraId} 
                       className="w-full h-full flex-1"
                       // Ajuste a URL se seu MediaMTX estiver em outro IP/Porta
                       mediaMtxUrl="http://localhost:8889" 
                     />
                     
                     {/* Overlay de carregamento enquanto o WebRTC negocia */}
                     {isActivating && (
                       <div className="absolute inset-0 z-20 bg-black/90 flex flex-col items-center justify-center text-white">
                         <Activity className="animate-spin mb-4 text-blue-500" size={48} />
                         <p className="text-lg font-semibold">Iniciando Processamento IA</p>
                         <p className="text-sm text-gray-400 mt-2 max-w-md text-center">
                           Carregando modelo YOLOv11 e gerando bounding boxes...
                         </p>
                       </div>
                     )}
                  </div>
                )}
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
                <div className="text-center text-gray-500">
                  <div className="bg-white p-4 rounded-full shadow-sm inline-block mb-4">
                    <Play size={48} className="text-blue-500 ml-1" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900">Selecione uma Câmera</h3>
                  <p className="max-w-md mx-auto mt-2 text-sm">
                    Clique em uma câmera na lista ao lado para iniciar a detecção em tempo real via WebRTC.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}