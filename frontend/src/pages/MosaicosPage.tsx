import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Settings, Play, Grid3X3, AlertCircle } from 'lucide-react'
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
import { mosaicoService, cameraService, streamingService } from '@/services/api'
import { useDynamicMosaic } from '@/hooks/useDynamicMosaic'
import type { Mosaico, Camera } from '@/types'

export function MosaicosPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [selectedMosaico, setSelectedMosaico] = useState<Mosaico | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)

  const { data: mosaicos, isLoading } = useQuery({
    queryKey: ['mosaicos'],
    queryFn: mosaicoService.list,
  })

  const { data: cameras } = useQuery({
    queryKey: ['cameras'],
    queryFn: cameraService.list,
  })

  const deleteMutation = useMutation({
    mutationFn: mosaicoService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mosaicos'] })
    },
  })

  const filteredMosaicos = mosaicos?.filter((mosaico) =>
    mosaico.name.toLowerCase().includes(search.toLowerCase())
  ) ?? []

  const handleDelete = (mosaico: Mosaico) => {
    if (confirm(`Remover mosaico "${mosaico.name}"?`)) {
      deleteMutation.mutate(mosaico.id)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Mosaicos</h1>
          <p className="text-muted-foreground">Visualize até 4 câmeras simultaneamente</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Criar Mosaico
        </Button>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Buscar mosaicos..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Mosaicos Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="aspect-video rounded-xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredMosaicos.map((mosaico) => (
            <MosaicoCard
              key={mosaico.id}
              mosaico={mosaico}
              onView={() => setSelectedMosaico(mosaico)}
              onDelete={() => handleDelete(mosaico)}
            />
          ))}
        </div>
      )}

      {/* Mosaico Viewer */}
      {selectedMosaico && (
        <MosaicoViewer
          mosaico={selectedMosaico}
          onClose={() => setSelectedMosaico(null)}
        />
      )}

      {/* Create Modal */}
      {showCreateModal && cameras && (
        <CreateMosaicoModal
          cameras={cameras}
          onClose={() => setShowCreateModal(false)}
        />
      )}
    </div>
  )
}

// Mosaico Card Component
function MosaicoCard({ 
  mosaico, 
  onView
}: { 
  mosaico: Mosaico
  onView: () => void
  onDelete: () => void 
}) {
  return (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <div className="aspect-video bg-black relative group cursor-pointer" onClick={onView}>
        <div className="grid grid-cols-2 grid-rows-2 h-full gap-1 p-2">
          {mosaico.cameras_positions.slice(0, 4).map((pos, index) => (
            <div key={index} className="bg-gray-800 rounded flex items-center justify-center">
              <div className="text-white text-xs text-center">
                <div className="text-lg mb-1">📹</div>
                <div className="truncate px-1">{pos.camera.name}</div>
              </div>
            </div>
          ))}
          {Array.from({ length: 4 - mosaico.cameras_positions.length }).map((_, index) => (
            <div key={`empty-${index}`} className="bg-gray-900 rounded flex items-center justify-center">
              <div className="text-gray-600 text-xs">Vazio</div>
            </div>
          ))}
        </div>
        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <Play className="w-12 h-12 text-white" />
        </div>
      </div>
      
      <CardContent className="p-4">
        <h3 className="font-semibold truncate">{mosaico.name}</h3>
        <p className="text-sm text-muted-foreground">
          {mosaico.cameras_positions.length} câmera(s)
        </p>
        
        <div className="flex gap-2 mt-3">
          <Button size="sm" variant="outline" className="flex-1" onClick={onView}>
            <Play className="w-3 h-3 mr-1" />
            Visualizar
          </Button>
          <Button size="sm" variant="outline">
            <Settings className="w-3 h-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

// Mosaico Viewer Component
function MosaicoViewer({ 
  mosaico, 
  onClose 
}: { 
  mosaico: Mosaico
  onClose: () => void 
}) {
  const { slots, activateSlot, activeCount } = useDynamicMosaic(4)
  const [error, setError] = useState<string | null>(null)
  const [streamUrls, setStreamUrls] = useState<Record<number, string>>({})
  const [maxStreams, setMaxStreams] = useState<number>(4)

  const handleActivateStream = async (cameraId: number, position: number) => {
    // Check limit before requesting stream
    if (activeCount >= maxStreams) {
      setError(`Limite de ${maxStreams} streams atingido`)
      return
    }

    try {
      setError(null)
      const response = await cameraService.getStream(cameraId)
      setStreamUrls(prev => ({ ...prev, [cameraId]: response.stream_url }))
      activateSlot(position, cameraId.toString())
    } catch (err: any) {
      if (err.response?.status === 429) {
        const data = err.response.data
        setMaxStreams(data.max_streams || 4)
        setError(`Limite de ${data.max_streams} streams atingido`)
      } else {
        setError('Erro ao iniciar stream')
      }
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/90" onClick={onClose} />
      <div className="relative w-full max-w-6xl bg-card rounded-xl overflow-hidden">
        <div className="p-4 border-b">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">{mosaico.name}</h2>
            {error && (
              <div className="flex items-center gap-2 text-red-500 text-sm">
                <AlertCircle className="w-4 h-4" />
                {error}
              </div>
            )}
          </div>
        </div>
        
        <div className="aspect-video bg-black p-4">
          <div className="grid grid-cols-2 grid-rows-2 h-full gap-2">
            {mosaico.cameras_positions.slice(0, 4).map((pos, index) => {
              const slot = slots[index]
              const streamUrl = streamUrls[pos.camera.id] || streamingService.getHlsUrl(pos.camera.id)
              
              return (
                <div key={index} className="bg-gray-900 rounded overflow-hidden relative">
                  {slot.streamActive ? (
                    <>
                      <VideoPlayer
                        src={streamUrl}
                        autoPlay
                        muted
                        className="h-full"
                      />
                      <div className="absolute bottom-2 left-2 bg-black/80 text-white text-xs px-2 py-1 rounded">
                        {pos.camera.name}
                      </div>
                    </>
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center">
                      <div className="text-gray-600 text-center">
                        <div className="text-lg mb-2">📹</div>
                        <div className="text-sm mb-3">{pos.camera.name}</div>
                        <Button
                          size="sm"
                          onClick={() => handleActivateStream(pos.camera.id, index)}
                        >
                          <Play className="w-3 h-3 mr-1" />
                          Iniciar
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
            {Array.from({ length: 4 - mosaico.cameras_positions.length }).map((_, index) => (
              <div key={`empty-${index}`} className="bg-gray-900 rounded flex items-center justify-center">
                <div className="text-gray-600">
                  <Grid3X3 className="w-8 h-8 mx-auto mb-2" />
                  <div className="text-sm">Posição vazia</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// Create Mosaico Modal
function CreateMosaicoModal({ 
  cameras, 
  onClose 
}: { 
  cameras: Camera[]
  onClose: () => void 
}) {
  const queryClient = useQueryClient()
  const [name, setName] = useState('')
  const [selectedCameras, setSelectedCameras] = useState<{ camera: Camera; position: number }[]>([])

  const createMutation = useMutation({
    mutationFn: async (data: { name: string; cameras: { camera_id: number; position: number }[] }) => {
      const mosaico = await mosaicoService.create({ name: data.name })
      await mosaicoService.updateCameras(mosaico.id, data.cameras)
      return mosaico
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mosaicos'] })
      onClose()
    },
  })

  const handleAddCamera = (camera: Camera) => {
    if (selectedCameras.length < 4 && !selectedCameras.find(sc => sc.camera.id === camera.id)) {
      setSelectedCameras(prev => [...prev, { camera, position: prev.length + 1 }])
    }
  }

  const handleRemoveCamera = (cameraId: number) => {
    setSelectedCameras(prev => 
      prev.filter(sc => sc.camera.id !== cameraId)
        .map((sc, index) => ({ ...sc, position: index + 1 }))
    )
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      name,
      cameras: selectedCameras.map(sc => ({ camera_id: sc.camera.id, position: sc.position }))
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <Card className="relative w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <CardHeader>
          <CardTitle>Criar Mosaico</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Nome do Mosaico</label>
              <Input
                placeholder="Ex: Área Externa"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div>
              <label className="text-sm font-medium">Câmeras Selecionadas ({selectedCameras.length}/4)</label>
              <div className="grid grid-cols-2 gap-2 mt-2 mb-4">
                {Array.from({ length: 4 }).map((_, index) => {
                  const camera = selectedCameras[index]
                  return (
                    <div key={index} className="aspect-video bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center">
                      {camera ? (
                        <div className="text-center p-2">
                          <div className="text-sm font-medium truncate">{camera.camera.name}</div>
                          <Button 
                            type="button"
                            size="sm" 
                            variant="outline" 
                            className="mt-1"
                            onClick={() => handleRemoveCamera(camera.camera.id)}
                          >
                            Remover
                          </Button>
                        </div>
                      ) : (
                        <div className="text-gray-500 text-sm">Posição {index + 1}</div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium">Câmeras Disponíveis</label>
              <div className="max-h-40 overflow-y-auto border rounded p-2 space-y-1">
                {cameras.map((camera) => (
                  <div key={camera.id} className="flex items-center justify-between p-2 hover:bg-gray-50 rounded">
                    <div>
                      <div className="font-medium">{camera.name}</div>
                      <div className="text-sm text-gray-500">{camera.location}</div>
                    </div>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={selectedCameras.length >= 4 || selectedCameras.some(sc => sc.camera.id === camera.id)}
                      onClick={() => handleAddCamera(camera)}
                    >
                      Adicionar
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-3 pt-4">
              <Button type="button" variant="outline" className="flex-1" onClick={onClose}>
                Cancelar
              </Button>
              <Button type="submit" className="flex-1" disabled={!name || selectedCameras.length === 0}>
                Criar Mosaico
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}