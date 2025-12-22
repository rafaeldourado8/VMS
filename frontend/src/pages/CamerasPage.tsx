import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, X, Loader2 } from 'lucide-react'
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Skeleton,
} from '@/components/ui'
import { CameraGrid } from '@/components/cameras/CameraGrid'
import { VideoPlayer } from '@/components/cameras/VideoPlayer'
import { cameraService, streamingService } from '@/services/api'
import type { Camera, CameraCreateRequest } from '@/types'

export function CamerasPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null)
  const [showAddModal, setShowAddModal] = useState(false)

  const { data: cameras, isLoading } = useQuery({
    queryKey: ['cameras'],
    queryFn: cameraService.list,
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
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="aspect-video rounded-xl" />
          ))}
        </div>
      ) : (
        <CameraGrid
          cameras={filteredCameras}
          onCameraClick={setSelectedCamera}
          onCameraDelete={handleDelete}
        />
      )}

      {/* Camera Detail Modal */}
      {selectedCamera && (
        <CameraDetailModal
          camera={selectedCamera}
          onClose={() => setSelectedCamera(null)}
        />
      )}

      {/* Add Camera Modal */}
      {showAddModal && (
        <AddCameraModal onClose={() => setShowAddModal(false)} />
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
  const hlsUrl = streamingService.getHlsUrl(camera.id)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <div className="relative w-full max-w-5xl bg-card rounded-xl overflow-hidden animate-slide-in">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div>
            <h2 className="text-lg font-semibold">{camera.name}</h2>
            {camera.location && (
              <p className="text-sm text-muted-foreground">{camera.location}</p>
            )}
          </div>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        {/* Video */}
        <div className="aspect-video bg-black">
          <VideoPlayer
            src={hlsUrl}
            autoPlay
            muted={false}
            className="h-full"
          />
        </div>

        {/* Info */}
        <div className="p-4 grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Status</p>
            <p className="font-medium capitalize">{camera.status}</p>
          </div>
          <div>
            <p className="text-muted-foreground">ID</p>
            <p className="font-medium font-mono">{camera.id}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Criada em</p>
            <p className="font-medium">
              {new Date(camera.created_at).toLocaleDateString('pt-BR')}
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Stream</p>
            <p className="font-medium font-mono text-xs truncate">
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
  const [formData, setFormData] = useState<CameraCreateRequest>({
    name: '',
    stream_url: '',
    location: '',
  })

  const createMutation = useMutation({
    mutationFn: async (data: CameraCreateRequest) => {
      // Criar câmera no Django
      const camera = await cameraService.create(data)
      // Provisionar no MediaMTX via Streaming Service
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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <Card className="relative w-full max-w-md animate-slide-in">
        <CardHeader>
          <CardTitle>Adicionar Câmera</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Nome</label>
              <Input
                placeholder="Ex: Entrada Principal"
                value={formData.name}
                onChange={(e) =>
                  setFormData((f) => ({ ...f, name: e.target.value }))
                }
                required
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">URL RTSP</label>
              <Input
                placeholder="rtsp://usuario:senha@ip:porta/stream"
                value={formData.stream_url}
                onChange={(e) =>
                  setFormData((f) => ({ ...f, stream_url: e.target.value }))
                }
                required
              />
              <p className="text-xs text-muted-foreground">
                Formato: rtsp://user:pass@192.168.1.100:554/stream
              </p>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Localização (opcional)</label>
              <Input
                placeholder="Ex: Portaria, Estacionamento"
                value={formData.location}
                onChange={(e) =>
                  setFormData((f) => ({ ...f, location: e.target.value }))
                }
              />
            </div>

            {createMutation.isError && (
              <div className="p-3 rounded-lg bg-destructive/10 text-sm text-destructive">
                Erro ao criar câmera. Verifique os dados e tente novamente.
              </div>
            )}

            <div className="flex gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                className="flex-1"
                onClick={onClose}
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                className="flex-1"
                disabled={createMutation.isPending}
              >
                {createMutation.isPending ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Criando...
                  </>
                ) : (
                  'Criar Câmera'
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
