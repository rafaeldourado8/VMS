import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, X, Loader2, Settings, Eye, Trash2, ChevronLeft, ChevronRight, Radio, MapPin, Calendar, Copy, Check, ArrowRight, ArrowLeft } from 'lucide-react'
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Skeleton,
} from '@/components/ui'
import { VideoPlayer } from '@/components/cameras/VideoPlayer'
import { StreamThumbnail } from '@/components/cameras/StreamThumbnail'
import { CameraConfig } from '@/components/cameras/DetectionConfig'
import { cameraService, streamingService } from '@/services/api'
import type { Camera, CameraCreateRequest, CameraEasyModeRequest } from '@/types'

const ITEMS_PER_PAGE = 10

export function CamerasPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)
  const [showDetectionConfig, setShowDetectionConfig] = useState<Camera | null>(null)
  const [currentPage, setCurrentPage] = useState(1)

  const { data: cameras, isLoading } = useQuery({
    queryKey: ['cameras'],
    queryFn: cameraService.list,
    staleTime: 30000,
    refetchInterval: 60000,
  })

  const deleteMutation = useMutation({
    mutationFn: cameraService.delete,
    onSuccess: (deletedCameraId) => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
      // Não precisa chamar removeCamera aqui pois o cache já foi limpo no serviço
    },
  })

  const filteredCameras = cameras?.filter((cam) =>
    cam.name.toLowerCase().includes(search.toLowerCase()) ||
    cam.location?.toLowerCase().includes(search.toLowerCase())
  ) ?? []

  const totalPages = Math.ceil(filteredCameras.length / ITEMS_PER_PAGE)
  const paginatedCameras = filteredCameras.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  )

  const handleDelete = (camera: Camera) => {
    if (confirm(`Remover câmera "${camera.name}"?`)) {
      deleteMutation.mutate(camera.id)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Câmeras</h1>
          <p className="text-muted-foreground">Gerencie suas câmeras de vigilância</p>
        </div>
        <Button onClick={() => setShowAddModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Adicionar Câmera
        </Button>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Buscar câmeras..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value)
            setCurrentPage(1)
          }}
          className="pl-10"
        />
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-20 rounded-xl" />
          ))}
        </div>
      ) : (
        <>
          <CameraList
            cameras={paginatedCameras}
            onCameraView={setSelectedCamera}
            onCameraConfig={setShowDetectionConfig}
            onCameraDelete={handleDelete}
          />
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Mostrando {(currentPage - 1) * ITEMS_PER_PAGE + 1} a {Math.min(currentPage * ITEMS_PER_PAGE, filteredCameras.length)} de {filteredCameras.length} câmeras
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                    <Button
                      key={page}
                      variant={currentPage === page ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setCurrentPage(page)}
                      className="w-8"
                    >
                      {page}
                    </Button>
                  ))}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Camera Detail Modal */}
      {selectedCamera && (
        <CameraDetailModal
          camera={selectedCamera}
          onClose={() => setSelectedCamera(null)}
        />
      )}

      {/* Detection Config Modal */}
      {showDetectionConfig && (
        <CameraConfig
          camera={showDetectionConfig}
          onClose={() => setShowDetectionConfig(null)}
        />
      )}

      {/* Add Camera Modal */}
      {showAddModal && (
        <AddCameraModal onClose={() => setShowAddModal(false)} />
      )}
    </div>
  )
}

// Camera List Component
function CameraList({
  cameras,
  onCameraView,
  onCameraConfig,
  onCameraDelete,
}: {
  cameras: Camera[]
  onCameraView: (camera: Camera) => void
  onCameraConfig: (camera: Camera) => void
  onCameraDelete: (camera: Camera) => void
}) {
  return (
    <div className="space-y-3">
      {cameras.map((camera) => (
        <Card key={camera.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <StreamThumbnail
                  cameraId={camera.id}
                  cameraName={camera.name}
                  cameraStatus={camera.status}
                  className="w-20 h-12 flex-shrink-0"
                  onClick={() => onCameraView(camera)}
                  showStatus={true}
                />
                <div>
                  <h3 className="font-semibold">{camera.name}</h3>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    {camera.location && (
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {camera.location}
                      </span>
                    )}
                    {camera.latitude && camera.longitude && (
                      <span className="text-xs">
                        ({camera.latitude.toFixed(4)}, {camera.longitude.toFixed(4)})
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-4 mt-1">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      camera.status === 'online' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {camera.status === 'online' ? 'Online' : 'Offline'}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      ID: {camera.id}
                    </span>
                    <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-600">
                      <Calendar className="w-3 h-3 inline mr-1" />
                      {camera.recording_retention_days || 30}d
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onCameraView(camera)}
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Visualizar
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onCameraConfig(camera)}
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Configurar
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onCameraDelete(camera)}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Remover
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
      
      {cameras.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Nenhuma câmera encontrada</p>
        </div>
      )}
    </div>
  )
}

// Camera Detail Modal
function CameraDetailModal({
  camera,
  onClose,
}: {
  camera: Camera
  onClose: () => void
}) {
  const [mode, setMode] = useState<'live' | 'playback'>('live')
  const [videoSrc, setVideoSrc] = useState(streamingService.getHlsUrl(camera.id))

  const goLive = () => {
    setMode('live')
    setVideoSrc(streamingService.getHlsUrl(camera.id))
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <div className="relative w-full max-w-5xl bg-white dark:bg-gray-900 rounded-xl overflow-hidden animate-slide-in shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
          <div>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">{camera.name}</h2>
            {camera.location && (
              <p className="text-sm text-gray-600 dark:text-gray-400">{camera.location}</p>
            )}
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Video */}
        <div className="relative aspect-video bg-black">
          <VideoPlayer
            src={videoSrc}
            autoPlay
            muted={false}
            showRecordingControls={true}
            cameraId={camera.id}
            className="h-full"
          />
          
          {mode === 'playback' && (
            <button
              onClick={goLive}
              className="absolute top-4 right-4 flex items-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors shadow-lg"
            >
              <Radio className="w-4 h-4" />
              Ao Vivo
            </button>
          )}
        </div>

        {/* Info */}
        <div className="p-4 grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm bg-white dark:bg-gray-900">
          <div>
            <p className="text-gray-600 dark:text-gray-400">Status</p>
            <p className="font-medium capitalize text-gray-900 dark:text-white">{camera.status}</p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-gray-400">ID</p>
            <p className="font-medium font-mono text-gray-900 dark:text-white">{camera.id}</p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-gray-400">Criada em</p>
            <p className="font-medium text-gray-900 dark:text-white">
              {new Date(camera.created_at).toLocaleDateString('pt-BR')}
            </p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-gray-400">Stream</p>
            <p className="font-medium font-mono text-xs truncate text-gray-900 dark:text-white">
              cam_{camera.id}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

// RTMP Server from env
const RTMP_SERVER = (import.meta as any).env?.VITE_RTMP_SERVER || 'localhost:1935'

// Easy Mode Wizard - Gerador de URL RTMP
function EasyModeWizard({ onClose, onBack }: { onClose: () => void; onBack: () => void }) {
  const queryClient = useQueryClient()
  const [step, setStep] = useState(1)
  const [copied, setCopied] = useState(false)
  const [createdCamera, setCreatedCamera] = useState<Camera | null>(null)
  const [locationType, setLocationType] = useState<'address' | 'coords' | 'url'>('address')
  const [easyFormData, setEasyFormData] = useState<CameraEasyModeRequest>({
    name: '',
    brand: '',
    location: '',
    latitude: undefined,
    longitude: undefined,
    recording_retention_days: 30,
  })
  const [modelName, setModelName] = useState('')

  const createMutation = useMutation({
    mutationFn: async (data: CameraEasyModeRequest) => {
      const camera = await cameraService.createEasyMode({ ...data, model_name: modelName || undefined })
      return camera
    },
    onSuccess: (camera) => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
      setCreatedCamera(camera)
      setStep(5)
    },
  })

  const rtmpUrl = createdCamera?.stream_key
    ? `rtmp://${RTMP_SERVER}/cam_${createdCamera.id}`
    : ''
  const streamKey = createdCamera?.stream_key || ''

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const canNext = () => {
    if (step === 1) return easyFormData.name.trim().length > 0
    if (step === 2) return easyFormData.brand.length > 0
    if (step === 3) return true
    if (step === 4) return true
    return false
  }

  const handleNext = () => {
    if (step === 4) {
      createMutation.mutate(easyFormData)
      return
    }
    setStep(s => s + 1)
  }

  const totalSteps = 5
  const stepLabels = ['Nome', 'Marca', 'Local', 'Plano', 'URL RTMP']

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <Card className="relative w-full max-w-lg animate-slide-in max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Modo Facil</span>
            <span className="text-sm font-normal text-muted-foreground">
              Passo {step} de {totalSteps}
            </span>
          </CardTitle>
          {/* Progress bar */}
          <div className="flex gap-1 mt-2">
            {stepLabels.map((label, i) => (
              <div key={i} className="flex-1 text-center">
                <div
                  className={`h-1.5 rounded-full mb-1 ${
                    i + 1 <= step ? 'bg-primary' : 'bg-muted'
                  }`}
                />
                <span className={`text-[10px] ${i + 1 === step ? 'text-primary font-semibold' : 'text-muted-foreground'}`}>
                  {label}
                </span>
              </div>
            ))}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">

          {/* Step 1: Nome */}
          {step === 1 && (
            <div className="space-y-3">
              <label className="text-sm font-medium">Nome da Camera</label>
              <Input
                placeholder="Ex: Entrada Principal"
                value={easyFormData.name}
                onChange={(e) => setEasyFormData(f => ({ ...f, name: e.target.value }))}
                autoFocus
              />
              <p className="text-xs text-muted-foreground">
                Escolha um nome que identifique a camera facilmente.
              </p>
            </div>
          )}

          {/* Step 2: Marca + Modelo */}
          {step === 2 && (
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Marca da Camera</label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { id: 'hikvision', label: 'Hikvision' },
                    { id: 'intelbras', label: 'Intelbras' },
                  ].map((b) => (
                    <Button
                      key={b.id}
                      type="button"
                      variant={easyFormData.brand === b.id ? 'default' : 'outline'}
                      onClick={() => setEasyFormData(f => ({ ...f, brand: b.id }))}
                      className="h-16 text-base"
                    >
                      {b.label}
                    </Button>
                  ))}
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Modelo <span className="text-muted-foreground font-normal">(opcional)</span>
                </label>
                <Input
                  placeholder="Ex: DS-2CD2043G2-I"
                  value={modelName}
                  onChange={(e) => setModelName(e.target.value)}
                />
              </div>
            </div>
          )}

          {/* Step 3: Localização */}
          {step === 3 && (
            <div className="space-y-3">
              <label className="text-sm font-medium">Localizacao</label>
              <div className="flex gap-2">
                <Button type="button" size="sm" variant={locationType === 'address' ? 'default' : 'outline'} onClick={() => setLocationType('address')}>
                  Endereco
                </Button>
                <Button type="button" size="sm" variant={locationType === 'coords' ? 'default' : 'outline'} onClick={() => setLocationType('coords')}>
                  Coordenadas
                </Button>
                <Button type="button" size="sm" variant={locationType === 'url' ? 'default' : 'outline'} onClick={() => setLocationType('url')}>
                  URL Maps
                </Button>
              </div>

              {locationType === 'address' && (
                <Input
                  placeholder="Ex: Rua ABC, 123 - Bairro"
                  value={easyFormData.location}
                  onChange={(e) => setEasyFormData(f => ({ ...f, location: e.target.value }))}
                />
              )}

              {locationType === 'coords' && (
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    type="number" step="any" placeholder="Latitude"
                    value={easyFormData.latitude || ''}
                    onChange={(e) => setEasyFormData(f => ({ ...f, latitude: parseFloat(e.target.value) || undefined }))}
                  />
                  <Input
                    type="number" step="any" placeholder="Longitude"
                    value={easyFormData.longitude || ''}
                    onChange={(e) => setEasyFormData(f => ({ ...f, longitude: parseFloat(e.target.value) || undefined }))}
                  />
                </div>
              )}

              {locationType === 'url' && (
                <>
                  <Input
                    placeholder="Cole a URL do Google Maps"
                    onChange={(e) => {
                      const url = e.target.value
                      const match = url.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/)
                      if (match) {
                        setEasyFormData(f => ({
                          ...f,
                          latitude: parseFloat(match[1]),
                          longitude: parseFloat(match[2]),
                          location: `${parseFloat(match[1]).toFixed(6)}, ${parseFloat(match[2]).toFixed(6)}`,
                        }))
                      }
                    }}
                  />
                  {easyFormData.latitude && easyFormData.longitude && (
                    <p className="text-xs text-green-600">
                      Coordenadas: {easyFormData.latitude}, {easyFormData.longitude}
                    </p>
                  )}
                </>
              )}
            </div>
          )}

          {/* Step 4: Retenção */}
          {step === 4 && (
            <div className="space-y-3">
              <label className="text-sm font-medium flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Retencao de Gravacao: <span className="text-blue-600 font-bold">{easyFormData.recording_retention_days} dias</span>
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[7, 15, 30].map((days) => (
                  <Button
                    key={days}
                    type="button"
                    variant={easyFormData.recording_retention_days === days ? 'default' : 'outline'}
                    onClick={() => setEasyFormData(prev => ({ ...prev, recording_retention_days: days }))}
                    className="h-14"
                  >
                    {days} dias
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* Step 5: Resultado - URL RTMP gerada */}
          {step === 5 && createdCamera && (
            <div className="space-y-4">
              <div className="p-4 rounded-lg bg-green-50 border border-green-200">
                <p className="text-sm font-semibold text-green-800 mb-1">Camera criada com sucesso!</p>
                <p className="text-xs text-green-700">Configure sua camera com os dados abaixo.</p>
              </div>

              {/* URL RTMP */}
              <div className="space-y-2">
                <label className="text-sm font-medium">URL do Servidor RTMP</label>
                <div className="flex gap-2">
                  <Input value={rtmpUrl} readOnly className="font-mono text-xs" />
                  <Button type="button" size="sm" variant="outline" onClick={() => handleCopy(rtmpUrl)}>
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </Button>
                </div>
              </div>

              {/* Stream Key */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Stream Key</label>
                <div className="flex gap-2">
                  <Input value={streamKey} readOnly className="font-mono text-xs" />
                  <Button type="button" size="sm" variant="outline" onClick={() => handleCopy(streamKey)}>
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </Button>
                </div>
              </div>

              {/* Instruções por marca */}
              <div className="p-4 rounded-lg bg-blue-50 border border-blue-200 space-y-2">
                <p className="text-sm font-semibold text-blue-800">
                  {createdCamera.brand === 'hikvision' ? 'Configuracao - Hikvision' : 'Configuracao - Intelbras'}
                </p>
                {createdCamera.brand === 'hikvision' ? (
                  <ol className="text-xs text-blue-700 space-y-1 list-decimal list-inside">
                    <li>Acesse a interface web da camera (http://IP-da-camera)</li>
                    <li>Va em <strong>Configuration &gt; Network &gt; Advanced Settings &gt; Platform Access</strong></li>
                    <li>Ou: <strong>Configuration &gt; Network &gt; TCP/IP &gt; RTMP</strong></li>
                    <li>Habilite o RTMP e cole a <strong>URL do Servidor</strong> acima</li>
                    <li>Cole a <strong>Stream Key</strong> no campo correspondente</li>
                    <li>Salve e a camera comecara a transmitir</li>
                  </ol>
                ) : (
                  <ol className="text-xs text-blue-700 space-y-1 list-decimal list-inside">
                    <li>Acesse a interface web do DVR/NVR (http://IP-do-DVR)</li>
                    <li>Va em <strong>Configuracoes &gt; Rede &gt; Plataforma</strong></li>
                    <li>Ou: <strong>Menu &gt; Rede &gt; RTMP</strong></li>
                    <li>Habilite o RTMP e cole a <strong>URL do Servidor</strong> acima</li>
                    <li>Cole a <strong>Stream Key</strong> no campo correspondente</li>
                    <li>Salve e a camera comecara a transmitir</li>
                  </ol>
                )}
              </div>
            </div>
          )}

          {/* Error */}
          {createMutation.isError && (
            <div className="p-3 rounded-lg bg-destructive/10 text-sm text-destructive">
              <p className="font-semibold">Erro ao criar camera</p>
              <p className="text-xs mt-1">
                {(createMutation.error as any)?.response?.data?.detail ||
                 (createMutation.error as any)?.response?.data?.name?.[0] ||
                 'Verifique os dados e tente novamente'}
              </p>
            </div>
          )}

          {/* Navigation */}
          <div className="flex gap-3 pt-2">
            {step < 5 ? (
              <>
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => step === 1 ? onBack() : setStep(s => s - 1)}
                >
                  <ArrowLeft className="w-4 h-4 mr-1" />
                  Voltar
                </Button>
                <Button
                  type="button"
                  className="flex-1"
                  disabled={!canNext() || createMutation.isPending}
                  onClick={handleNext}
                >
                  {createMutation.isPending ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Criando...</>
                  ) : step === 4 ? (
                    <>Criar Camera</>
                  ) : (
                    <>Proximo <ArrowRight className="w-4 h-4 ml-1" /></>
                  )}
                </Button>
              </>
            ) : (
              <Button type="button" className="w-full" onClick={onClose}>
                Concluir
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Add Camera Modal
function AddCameraModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [mode, setMode] = useState<'select' | 'easy' | 'advanced'>('select')
  const [formData, setFormData] = useState<CameraCreateRequest>({
    name: '',
    stream_url: '',
    location: '',
    latitude: undefined,
    longitude: undefined,
    recording_retention_days: 30,
  })
  const [locationType, setLocationType] = useState<'address' | 'coords' | 'url'>('address')

  const createMutation = useMutation({
    mutationFn: async (data: CameraCreateRequest) => {
      console.log('Creating camera with data:', data)
      const camera = await cameraService.create(data)
      return camera
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
      onClose()
    },
    onError: (error: any) => {
      console.error('Error creating camera:', error.response?.data || error.message)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    // Garantir que location seja sempre string
    const locationValue = Array.isArray(formData.location) 
      ? formData.location[0] || '' 
      : formData.location || ''
    
    // Limpar campos vazios
    const cleanData: CameraCreateRequest = {
      name: formData.name.trim(),
      stream_url: formData.stream_url.trim(),
      location: locationValue.trim(),
      recording_retention_days: formData.recording_retention_days ?? 30,
    }
    
    // Adicionar coordenadas se existirem
    if (formData.latitude && !isNaN(formData.latitude)) cleanData.latitude = formData.latitude
    if (formData.longitude && !isNaN(formData.longitude)) cleanData.longitude = formData.longitude
    
    console.log('Submitting camera data:', cleanData)
    console.log('Recording retention days:', cleanData.recording_retention_days)
    createMutation.mutate(cleanData)
  }

  if (mode === 'select') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
        <div className="absolute inset-0 bg-black/80" onClick={onClose} />
        <Card className="relative w-full max-w-md animate-slide-in">
          <CardHeader>
            <CardTitle>Adicionar Câmera</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              onClick={() => setMode('easy')}
              className="w-full h-20 text-lg"
              variant="outline"
            >
              <div>
                <div className="font-semibold">Modo Fácil</div>
                <div className="text-xs text-muted-foreground">Gera URL RTMP automaticamente</div>
              </div>
            </Button>
            <Button
              onClick={() => setMode('advanced')}
              className="w-full h-20 text-lg"
              variant="outline"
            >
              <div>
                <div className="font-semibold">Modo Avançado</div>
                <div className="text-xs text-muted-foreground">URL completa</div>
              </div>
            </Button>
            <Button onClick={onClose} variant="ghost" className="w-full">
              Cancelar
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (mode === 'easy') {
    return <EasyModeWizard onClose={onClose} onBack={() => setMode('select')} />
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <Card className="relative w-full max-w-md animate-slide-in max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <CardTitle>Modo Avançado</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Nome</label>
              <Input
                placeholder="Ex: Entrada Principal"
                value={formData.name}
                onChange={(e) => setFormData(f => ({ ...f, name: e.target.value }))}
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">URL do Stream</label>
              <Input
                placeholder="rtsp://usuario:senha@ip:porta/stream"
                value={formData.stream_url}
                onChange={(e) => setFormData(f => ({ ...f, stream_url: e.target.value }))}
                required
              />
              <p className="text-xs text-muted-foreground">
                RTSP, RTMP, HTTP ou qualquer URL suportada
              </p>
            </div>

            {/* Localização */}
            <div className="space-y-3">
              <label className="text-sm font-medium">Localização</label>
              <div className="flex gap-2">
                <Button
                  type="button"
                  size="sm"
                  variant={locationType === 'address' ? 'default' : 'outline'}
                  onClick={() => setLocationType('address')}
                >
                  Endereço
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant={locationType === 'coords' ? 'default' : 'outline'}
                  onClick={() => setLocationType('coords')}
                >
                  Coordenadas
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant={locationType === 'url' ? 'default' : 'outline'}
                  onClick={() => setLocationType('url')}
                >
                  URL Maps
                </Button>
              </div>

              {locationType === 'address' && (
                <Input
                  placeholder="Ex: Rua ABC, 123 - Bairro"
                  value={formData.location}
                  onChange={(e) => setFormData(f => ({ ...f, location: e.target.value }))}
                />
              )}

              {locationType === 'coords' && (
                <div className="grid grid-cols-2 gap-2">
                  <Input
                    type="number"
                    step="any"
                    placeholder="Latitude"
                    value={formData.latitude || ''}
                    onChange={(e) => setFormData(f => ({ ...f, latitude: parseFloat(e.target.value) || undefined }))}
                  />
                  <Input
                    type="number"
                    step="any"
                    placeholder="Longitude"
                    value={formData.longitude || ''}
                    onChange={(e) => setFormData(f => ({ ...f, longitude: parseFloat(e.target.value) || undefined }))}
                  />
                </div>
              )}

              {locationType === 'url' && (
                <>
                  <Input
                    placeholder="Cole a URL do Google Maps"
                    onChange={(e) => {
                      const url = e.target.value
                      const match = url.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/)
                      if (match) {
                        const lat = parseFloat(match[1])
                        const lng = parseFloat(match[2])
                        setFormData(f => ({ 
                          ...f, 
                          latitude: lat, 
                          longitude: lng,
                          location: `${lat.toFixed(6)}, ${lng.toFixed(6)}`
                        }))
                      }
                    }}
                  />
                  {formData.latitude && formData.longitude && (
                    <p className="text-xs text-green-600">
                      ✓ Coordenadas: {formData.latitude}, {formData.longitude}
                    </p>
                  )}
                </>
              )}
            </div>

            {/* Retenção de Gravação */}
            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                Retenção de Gravação: <span className="text-blue-600 font-bold">{formData.recording_retention_days} dias</span>
              </label>
              <div className="grid grid-cols-3 gap-2">
                {[7, 15, 30].map((days) => (
                  <Button
                    key={days}
                    type="button"
                    variant={formData.recording_retention_days === days ? 'default' : 'outline'}
                    onClick={() => setFormData(prev => ({ ...prev, recording_retention_days: days }))}
                  >
                    {days} dias
                  </Button>
                ))}
              </div>
            </div>

            {createMutation.isError && (
              <div className="p-3 rounded-lg bg-destructive/10 text-sm text-destructive">
                <p className="font-semibold">Erro ao criar câmera</p>
                <p className="text-xs mt-1">
                  {(createMutation.error as any)?.response?.data?.detail || 
                   (createMutation.error as any)?.response?.data?.name?.[0] ||
                   (createMutation.error as any)?.response?.data?.stream_url?.[0] ||
                   'Verifique os dados e tente novamente'}
                </p>
              </div>
            )}

            <div className="flex gap-3">
              <Button type="button" variant="outline" className="flex-1" onClick={() => setMode('select')}>
                Voltar
              </Button>
              <Button type="submit" className="flex-1" disabled={createMutation.isPending}>
                {createMutation.isPending ? (
                  <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Criando...</>
                ) : 'Criar Câmera'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
