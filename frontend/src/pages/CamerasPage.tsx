import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, X, Loader2, Settings, Eye, Trash2, ChevronLeft, ChevronRight, Radio } from 'lucide-react'
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
import type { Camera, CameraCreateRequest } from '@/types'

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
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
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
                  <p className="text-sm text-muted-foreground">{camera.location || 'Sem localização'}</p>
                  <div className="flex items-center gap-4 mt-1">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      camera.status === 'online' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {camera.status === 'online' ? 'Online' : 'Offline'}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      camera.ai_enabled 
                        ? 'bg-blue-100 text-blue-800' 
                        : 'bg-gray-100 text-gray-600'
                    }`}>
                      IA {camera.ai_enabled ? 'Ativa' : 'Inativa'}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      ID: {camera.id}
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

// Add Camera Modal
function AddCameraModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [mode, setMode] = useState<'select' | 'easy' | 'advanced'>('select')
  const [protocol, setProtocol] = useState<'rtsp' | 'rtmp' | 'ip' | 'p2'>('rtsp')
  const [formData, setFormData] = useState<CameraCreateRequest>({
    name: '',
    stream_url: '',
    location: '',
  })

  const createMutation = useMutation({
    mutationFn: async (data: CameraCreateRequest) => {
      const camera = await cameraService.create(data)
      await streamingService.provisionCamera(camera.id, data.stream_url, data.name)
      return camera
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(formData)
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
                <div className="text-xs text-muted-foreground">Configuração guiada</div>
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
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
        <div className="absolute inset-0 bg-black/80" onClick={onClose} />
        <Card className="relative w-full max-w-md animate-slide-in">
          <CardHeader>
            <CardTitle>Modo Fácil - Selecione o Protocolo</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Protocolo</label>
                <div className="grid grid-cols-2 gap-2">
                  {(['rtsp', 'rtmp', 'ip', 'p2'] as const).map((p) => (
                    <Button
                      key={p}
                      type="button"
                      variant={protocol === p ? 'default' : 'outline'}
                      onClick={() => setProtocol(p)}
                      className="h-16"
                    >
                      {p === 'ip' ? 'IP/HTTP' : p === 'p2' ? 'P2P' : p.toUpperCase()}
                    </Button>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Nome</label>
                <Input
                  placeholder="Ex: Entrada Principal"
                  value={formData.name}
                  onChange={(e) => setFormData(f => ({ ...f, name: e.target.value }))}
                  required
                />
              </div>

              {protocol === 'rtsp' && (
                <div className="space-y-2">
                  <label className="text-sm font-medium">URL RTSP</label>
                  <Input
                    placeholder="rtsp://usuario:senha@192.168.1.100:554/stream"
                    value={formData.stream_url}
                    onChange={(e) => setFormData(f => ({ ...f, stream_url: e.target.value }))}
                    required
                  />
                </div>
              )}

              {protocol === 'rtmp' && (
                <div className="space-y-2">
                  <label className="text-sm font-medium">URL RTMP</label>
                  <Input
                    placeholder="rtmp://192.168.1.100:1935/live/stream"
                    value={formData.stream_url}
                    onChange={(e) => setFormData(f => ({ ...f, stream_url: e.target.value }))}
                    required
                  />
                </div>
              )}

              {protocol === 'ip' && (
                <>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">IP</label>
                      <Input
                        placeholder="192.168.1.100"
                        onChange={(e) => {
                          const ip = e.target.value
                          const port = document.getElementById('port-input') as HTMLInputElement
                          const user = document.getElementById('user-input') as HTMLInputElement
                          const pass = document.getElementById('pass-input') as HTMLInputElement
                          const path = document.getElementById('path-input') as HTMLInputElement
                          setFormData(f => ({ 
                            ...f, 
                            stream_url: `rtsp://${user?.value || 'admin'}:${pass?.value || 'admin'}@${ip}:${port?.value || '554'}${path?.value || '/stream'}` 
                          }))
                        }}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Porta</label>
                      <Input
                        id="port-input"
                        placeholder="554"
                        defaultValue="554"
                        onChange={(e) => {
                          const port = e.target.value
                          const ip = (document.querySelector('input[placeholder="192.168.1.100"]') as HTMLInputElement)?.value
                          const user = document.getElementById('user-input') as HTMLInputElement
                          const pass = document.getElementById('pass-input') as HTMLInputElement
                          const path = document.getElementById('path-input') as HTMLInputElement
                          if (ip) setFormData(f => ({ 
                            ...f, 
                            stream_url: `rtsp://${user?.value || 'admin'}:${pass?.value || 'admin'}@${ip}:${port}${path?.value || '/stream'}` 
                          }))
                        }}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Usuário</label>
                      <Input
                        id="user-input"
                        placeholder="admin"
                        defaultValue="admin"
                        onChange={(e) => {
                          const user = e.target.value
                          const ip = (document.querySelector('input[placeholder="192.168.1.100"]') as HTMLInputElement)?.value
                          const port = document.getElementById('port-input') as HTMLInputElement
                          const pass = document.getElementById('pass-input') as HTMLInputElement
                          const path = document.getElementById('path-input') as HTMLInputElement
                          if (ip) setFormData(f => ({ 
                            ...f, 
                            stream_url: `rtsp://${user}:${pass?.value || 'admin'}@${ip}:${port?.value || '554'}${path?.value || '/stream'}` 
                          }))
                        }}
                      />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Senha</label>
                      <Input
                        id="pass-input"
                        type="password"
                        placeholder="admin"
                        defaultValue="admin"
                        onChange={(e) => {
                          const pass = e.target.value
                          const ip = (document.querySelector('input[placeholder="192.168.1.100"]') as HTMLInputElement)?.value
                          const port = document.getElementById('port-input') as HTMLInputElement
                          const user = document.getElementById('user-input') as HTMLInputElement
                          const path = document.getElementById('path-input') as HTMLInputElement
                          if (ip) setFormData(f => ({ 
                            ...f, 
                            stream_url: `rtsp://${user?.value || 'admin'}:${pass}@${ip}:${port?.value || '554'}${path?.value || '/stream'}` 
                          }))
                        }}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Path (opcional)</label>
                    <Input
                      id="path-input"
                      placeholder="/stream"
                      defaultValue="/stream"
                      onChange={(e) => {
                        const path = e.target.value
                        const ip = (document.querySelector('input[placeholder="192.168.1.100"]') as HTMLInputElement)?.value
                        const port = document.getElementById('port-input') as HTMLInputElement
                        const user = document.getElementById('user-input') as HTMLInputElement
                        const pass = document.getElementById('pass-input') as HTMLInputElement
                        if (ip) setFormData(f => ({ 
                          ...f, 
                          stream_url: `rtsp://${user?.value || 'admin'}:${pass?.value || 'admin'}@${ip}:${port?.value || '554'}${path}` 
                        }))
                      }}
                    />
                    <p className="text-xs text-muted-foreground">
                      Ex: /stream, /cam/realmonitor?channel=1&subtype=0
                    </p>
                  </div>
                  <div className="p-2 rounded bg-gray-50 text-xs font-mono break-all">
                    {formData.stream_url || 'rtsp://admin:admin@IP:554/stream'}
                  </div>
                </>
              )}

              {protocol === 'p2' && (
                <>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">ID P2P</label>
                    <Input
                      placeholder="XXXXX-XXXXX-XXXXX"
                      onChange={(e) => setFormData(f => ({ ...f, stream_url: e.target.value }))}
                      required
                    />
                  </div>
                  <div className="p-3 rounded-lg bg-yellow-50 text-sm text-yellow-800">
                    ⚠️ P2P requer gateway externo. Insira a URL RTSP do gateway.
                  </div>
                </>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium">Localização (opcional)</label>
                <Input
                  placeholder="Ex: Portaria"
                  value={formData.location}
                  onChange={(e) => setFormData(f => ({ ...f, location: e.target.value }))}
                />
              </div>

              {createMutation.isError && (
                <div className="p-3 rounded-lg bg-destructive/10 text-sm text-destructive">
                  Erro ao criar câmera. Verifique os dados.
                </div>
              )}

              <div className="flex gap-3">
                <Button type="button" variant="outline" className="flex-1" onClick={() => setMode('select')}>
                  Voltar
                </Button>
                <Button type="submit" className="flex-1" disabled={createMutation.isPending}>
                  {createMutation.isPending ? (
                    <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Criando...</>
                  ) : 'Criar'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <Card className="relative w-full max-w-md animate-slide-in">
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

            <div className="space-y-2">
              <label className="text-sm font-medium">Localização (opcional)</label>
              <Input
                placeholder="Ex: Portaria, Estacionamento"
                value={formData.location}
                onChange={(e) => setFormData(f => ({ ...f, location: e.target.value }))}
              />
            </div>

            {createMutation.isError && (
              <div className="p-3 rounded-lg bg-destructive/10 text-sm text-destructive">
                Erro ao criar câmera. Verifique os dados.
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
