import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Play, Square, Eye, Settings, AlertCircle, CheckCircle } from 'lucide-react'
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui'
import { VideoPlayer } from '@/components/cameras/VideoPlayer'
import { aiService, cameraService } from '@/services/api'

const TEST_CAMERAS = [
  { name: 'Câmera 1', url: 'rtsp://admin:Camerite123@45.236.226.75:6053/cam/realmonitor?channel=1&subtype=0' },
  { name: 'Câmera 2', url: 'rtsp://admin:Camerite123@45.236.226.75:6052/cam/realmonitor?channel=1&subtype=0' },
  { name: 'Câmera 3', url: 'rtsp://admin:Camerite123@45.236.226.74:6050/cam/realmonitor?channel=1&subtype=0' },
  { name: 'Câmera 4', url: 'rtsp://admin:Camerite123@45.236.226.72:6049/cam/realmonitor?channel=1&subtype=0' },
  { name: 'Câmera 5', url: 'rtsp://admin:Camerite123@45.236.226.72:6048/cam/realmonitor?channel=1&subtype=0' },
]

export function AITestPage() {
  const [selectedCamera, setSelectedCamera] = useState<any>(null)
  const [testResults, setTestResults] = useState<Record<string, any>>({})
  const [isTestingAll, setIsTestingAll] = useState(false)

  const { data: detections, refetch: refetchDetections } = useQuery({
    queryKey: ['detections'],
    queryFn: () => fetch('/api/detections/').then(res => res.json()),
    refetchInterval: 2000, // Atualiza a cada 2 segundos
  })

  const testCameraMutation = useMutation({
    mutationFn: async ({ cameraUrl, cameraName }: { cameraUrl: string, cameraName: string }) => {
      // Simular criação de câmera temporária para teste
      const tempCamera = await cameraService.create({
        name: `TESTE_${cameraName}`,
        stream_url: cameraUrl,
        location: 'Teste IA'
      })
      
      // Configurar ROI básico para teste
      await cameraService.updateDetectionConfig(tempCamera.id, {
        roi_areas: [{
          id: '1',
          name: 'Área Teste',
          points: [
            { x: 0.1, y: 0.1 },
            { x: 0.9, y: 0.1 },
            { x: 0.9, y: 0.9 },
            { x: 0.1, y: 0.9 }
          ],
          enabled: true
        }],
        virtual_lines: [],
        tripwires: [],
        zone_triggers: [],
        ai_enabled: true
      })

      // Iniciar processamento IA
      await aiService.startProcessing(tempCamera.id)
      
      return tempCamera
    },
    onSuccess: (camera, variables) => {
      setTestResults(prev => ({
        ...prev,
        [variables.cameraName]: { 
          status: 'testing', 
          camera,
          startTime: Date.now()
        }
      }))
    }
  })

  const testAllCameras = async () => {
    setIsTestingAll(true)
    setTestResults({})
    
    for (const camera of TEST_CAMERAS) {
      try {
        await testCameraMutation.mutateAsync({
          cameraUrl: camera.url,
          cameraName: camera.name
        })
        // Aguardar 2 segundos entre cada câmera
        await new Promise(resolve => setTimeout(resolve, 2000))
      } catch (error) {
        setTestResults(prev => ({
          ...prev,
          [camera.name]: { status: 'error', error: error.message }
        }))
      }
    }
    
    setIsTestingAll(false)
  }

  // Verificar detecções em tempo real
  useEffect(() => {
    if (detections?.results) {
      const newDetections = detections.results.filter(d => 
        d.camera_name?.startsWith('TESTE_')
      )
      
      newDetections.forEach(detection => {
        const cameraName = detection.camera_name.replace('TESTE_', '')
        setTestResults(prev => ({
          ...prev,
          [cameraName]: {
            ...prev[cameraName],
            status: 'detected',
            detection,
            detectionTime: Date.now()
          }
        }))
      })
    }
  }, [detections])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Teste de IA - Detecção de Placas</h1>
          <p className="text-muted-foreground">Testando detecção em câmeras reais</p>
        </div>
        <Button onClick={testAllCameras} disabled={isTestingAll}>
          {isTestingAll ? 'Testando...' : 'Testar Todas as Câmeras'}
        </Button>
      </div>

      {/* Status Geral */}
      <Card>
        <CardHeader>
          <CardTitle>Status do Teste</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {Object.keys(testResults).length}
              </div>
              <div className="text-sm text-muted-foreground">Câmeras Testadas</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {Object.values(testResults).filter(r => r.status === 'detected').length}
              </div>
              <div className="text-sm text-muted-foreground">Detecções Encontradas</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {Object.values(testResults).filter(r => r.status === 'error').length}
              </div>
              <div className="text-sm text-muted-foreground">Erros</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Câmeras */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {TEST_CAMERAS.map((camera) => {
          const result = testResults[camera.name]
          return (
            <Card key={camera.name} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{camera.name}</CardTitle>
                  {result?.status === 'testing' && (
                    <div className="flex items-center text-blue-600">
                      <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full mr-2" />
                      Testando
                    </div>
                  )}
                  {result?.status === 'detected' && (
                    <div className="flex items-center text-green-600">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Detectado
                    </div>
                  )}
                  {result?.status === 'error' && (
                    <div className="flex items-center text-red-600">
                      <AlertCircle className="w-4 h-4 mr-2" />
                      Erro
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="text-xs text-muted-foreground font-mono truncate">
                    {camera.url}
                  </div>
                  
                  {result?.detection && (
                    <div className="bg-green-50 p-3 rounded">
                      <div className="text-sm font-medium text-green-800">
                        Placa Detectada: {result.detection.plate || 'N/A'}
                      </div>
                      <div className="text-xs text-green-600">
                        Confiança: {result.detection.confidence}%
                      </div>
                      <div className="text-xs text-green-600">
                        Veículo: {result.detection.vehicle_type}
                      </div>
                      {result.detection.image_url && (
                        <img 
                          src={result.detection.image_url} 
                          alt="Detecção"
                          className="mt-2 w-full h-20 object-cover rounded"
                        />
                      )}
                    </div>
                  )}

                  {result?.error && (
                    <div className="bg-red-50 p-3 rounded">
                      <div className="text-sm text-red-800">
                        Erro: {result.error}
                      </div>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => setSelectedCamera({ ...camera, result })}
                    >
                      <Eye className="w-3 h-3 mr-1" />
                      Ver Stream
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => testCameraMutation.mutate({
                        cameraUrl: camera.url,
                        cameraName: camera.name
                      })}
                      disabled={result?.status === 'testing'}
                    >
                      <Play className="w-3 h-3 mr-1" />
                      Testar
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Detecções Recentes */}
      {detections?.results && (
        <Card>
          <CardHeader>
            <CardTitle>Detecções em Tempo Real</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 max-h-60 overflow-y-auto">
              {detections.results
                .filter(d => d.camera_name?.startsWith('TESTE_'))
                .slice(0, 10)
                .map((detection, index) => (
                <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 rounded">
                  {detection.image_url && (
                    <img 
                      src={detection.image_url} 
                      alt="Detecção"
                      className="w-16 h-12 object-cover rounded"
                    />
                  )}
                  <div className="flex-1">
                    <div className="font-medium">
                      {detection.camera_name.replace('TESTE_', '')}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Placa: {detection.plate || 'N/A'} | 
                      Confiança: {detection.confidence}% |
                      Veículo: {detection.vehicle_type}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {new Date(detection.timestamp).toLocaleString('pt-BR')}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modal de Visualização */}
      {selectedCamera && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80">
          <div className="relative w-full max-w-4xl bg-white rounded-xl overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-lg font-semibold">{selectedCamera.name}</h2>
              <Button variant="ghost" onClick={() => setSelectedCamera(null)}>
                ✕
              </Button>
            </div>
            <div className="aspect-video bg-black">
              <VideoPlayer
                src={selectedCamera.url}
                autoPlay
                muted={false}
                className="h-full"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}