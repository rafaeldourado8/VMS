import { useState, useEffect } from 'react';
import { Activity } from 'lucide-react';
import { useCameraStore } from '@/store/cameraStore';
import { detectionService, cameraService, streamingService } from '@/services/api';
import { VideoPlayer } from '@/components/cameras/VideoPlayer';

export default function LiveDetectionsPage() {
  const { cameras, setCameras } = useCameraStore();
  const [selectedCamera, setSelectedCamera] = useState<number | null>(null);
  const [detections, setDetections] = useState<any[]>([]);

  // Load cameras
  useEffect(() => {
    const loadCameras = async () => {
      try {
        const data = await cameraService.list();
        setCameras(data);
      } catch (err) {
        console.error('Erro carregando câmeras:', err);
      }
    };
    loadCameras();
  }, [setCameras]);

  // Load detections
  useEffect(() => {
    if (!selectedCamera) return;
    
    const loadDetections = async () => {
      try {
        const data = await detectionService.list({ camera_id: selectedCamera, page: 1 });
        setDetections(data.results || []);
      } catch (err) {
        console.error('Erro carregando detecções:', err);
      }
    };
    
    loadDetections();
    const interval = setInterval(loadDetections, 5000);
    return () => clearInterval(interval);
  }, [selectedCamera]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Detecções ao Vivo</h1>
          <p className="text-gray-600">Monitoramento em tempo real com IA</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="font-semibold mb-4">Câmeras</h2>
          <div className="space-y-2">
            {cameras.length === 0 ? (
              <div className="text-center text-gray-500 py-4 text-sm">
                Nenhuma câmera cadastrada
              </div>
            ) : (
              cameras.map(cam => (
                <button
                  key={cam.id}
                  onClick={() => setSelectedCamera(cam.id)}
                  className={`w-full text-left px-3 py-2 rounded transition ${
                    selectedCamera === cam.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 hover:bg-gray-200'
                  }`}
                >
                  <div className="font-medium">{cam.name}</div>
                  <div className="text-xs opacity-75">{cam.location || 'Sem localização'}</div>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="col-span-3 bg-white rounded-lg shadow p-4">
          {selectedCamera ? (
            <>
              <div className="mb-4">
                <h2 className="text-xl font-semibold">
                  {cameras.find(c => c.id === selectedCamera)?.name}
                </h2>
              </div>
              
              <VideoPlayer 
                src={streamingService.getHlsUrl(selectedCamera)}
                autoPlay
                muted={false}
                className="aspect-video"
              />
              
              <div className="mt-4">
                <div className="flex items-center gap-2 mb-3">
                  <Activity className="text-blue-600" size={18} />
                  <h3 className="font-semibold">Detecções Recentes</h3>
                </div>
                
                <div className="space-y-2 max-h-[300px] overflow-y-auto">
                  {detections.length === 0 ? (
                    <div className="text-center text-gray-500 py-4 text-sm">
                      Nenhuma detecção ainda
                    </div>
                  ) : (
                    detections.map((det, idx) => (
                      <div
                        key={idx}
                        className="border rounded-lg p-2 hover:bg-gray-50 transition flex items-center gap-3"
                      >
                        <img
                          src={det.snapshot_url}
                          alt={det.placa}
                          className="w-16 h-16 object-cover rounded"
                        />
                        <div className="flex-1">
                          <div className="font-bold">{det.placa}</div>
                          <div className="text-xs text-gray-500">
                            {new Date(det.data_hora).toLocaleString('pt-BR')}
                          </div>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded whitespace-nowrap ${
                          det.confianca > 0.9
                            ? 'bg-green-100 text-green-800'
                            : det.confianca > 0.7
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {(det.confianca * 100).toFixed(0)}%
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="aspect-video flex items-center justify-center bg-gray-100 rounded-lg">
              <div className="text-center text-gray-500">
                <Activity size={48} className="mx-auto mb-2 opacity-50" />
                <p>Selecione uma câmera</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
