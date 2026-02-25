import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, Play, Download, Trash2, Calendar, Clock, Scissors, X } from 'lucide-react'
import {
  Button,
  Input,
  Card,
  CardContent,
  Skeleton,
  Label,
} from '@/components/ui'
import { clipService, recordingService } from '@/services/api'
import type { Clip, Camera } from '@/types'

export function ClipsPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [selectedClip, setSelectedClip] = useState<Clip | null>(null)
  const [showCreateClip, setShowCreateClip] = useState(false)

  const { data: clips, isLoading } = useQuery({
    queryKey: ['clips'],
    queryFn: clipService.list,
  })

  const deleteMutation = useMutation({
    mutationFn: clipService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clips'] })
    },
  })

  const filteredClips = (clips || []).filter((clip) =>
    clip.name?.toLowerCase().includes(search.toLowerCase()) ||
    clip.camera_name?.toLowerCase().includes(search.toLowerCase())
  )

  const handleDelete = (clip: Clip) => {
    if (confirm(`Remover clip "${clip.name}"?`)) {
      deleteMutation.mutate(clip.id)
    }
  }

  const handleDownload = async (clip: Clip) => {
    const url = clip.video_url || `/api/clips/clips/${clip.id}/video/`
    const link = document.createElement('a')
    link.href = url
    link.download = `${clip.name}.mp4`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Meus Clips</h1>
          <p className="text-muted-foreground">Clips salvos e protegidos contra retenção automática</p>
        </div>
        <Button onClick={() => setShowCreateClip(true)}>
          <Scissors className="w-4 h-4 mr-2" />
          Criar Clip
        </Button>
      </div>

      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Buscar clips..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="aspect-video rounded-xl" />
          ))}
        </div>
      ) : filteredClips.length === 0 ? (
        <Card className="p-12 text-center">
          <Scissors className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">Nenhum clip encontrado</h3>
          <p className="text-muted-foreground">Crie clips de momentos importantes das suas gravações</p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredClips.map((clip) => (
            <Card key={clip.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-video bg-black relative group cursor-pointer"
                   onClick={() => setSelectedClip(clip)}>
                {clip.thumbnail_path ? (
                  <img 
                    src={clip.thumbnail_path} 
                    alt={clip.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Play className="w-12 h-12 text-white/60" />
                  </div>
                )}
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <Play className="w-12 h-12 text-white" />
                </div>
                <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded">
                  {formatDuration(clip.duration_seconds)}
                </div>
              </div>
              
              <CardContent className="p-4">
                <h3 className="font-semibold truncate">{clip.name}</h3>
                <p className="text-sm text-muted-foreground truncate">{clip.camera_name || 'Câmera removida'}</p>
                
                {clip.status && clip.status !== 'completed' && (
                  <div className="mt-2 text-xs">
                    <span className={`px-2 py-1 rounded ${
                      clip.status === 'processing' ? 'bg-blue-500/20 text-blue-400' :
                      clip.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {clip.status === 'processing' ? 'Processando...' :
                       clip.status === 'pending' ? 'Aguardando...' : 'Erro'}
                    </span>
                  </div>
                )}
                
                <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(clip.created_at).toLocaleDateString('pt-BR')}
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {formatDuration(clip.duration_seconds)}
                  </div>
                </div>

                <div className="flex gap-2 mt-3">
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => setSelectedClip(clip)}
                    disabled={clip.status !== 'completed' && clip.status !== undefined}
                  >
                    <Play className="w-3 h-3 mr-1" />
                    Assistir
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleDownload(clip)}
                    disabled={clip.status !== 'completed' && clip.status !== undefined}
                  >
                    <Download className="w-3 h-3" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleDelete(clip)}
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {selectedClip && (
        <ClipPlayerModal
          clip={selectedClip}
          onClose={() => setSelectedClip(null)}
        />
      )}

      {showCreateClip && (
        <CreateClipModal onClose={() => setShowCreateClip(false)} />
      )}
    </div>
  )
}

function ClipPlayerModal({ clip, onClose }: { clip: Clip; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/80" />
      <div className="relative w-full max-w-4xl bg-card rounded-xl overflow-hidden" onClick={(e) => e.stopPropagation()}>
        <div className="aspect-video bg-black">
          <video
            src={clip.video_url || `/api/clips/clips/${clip.id}/video/`}
            controls
            autoPlay
            className="w-full h-full"
          />
        </div>
        <div className="p-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">{clip.name}</h2>
            <p className="text-sm text-muted-foreground">{clip.camera_name || 'Câmera removida'}</p>
            <p className="text-xs text-muted-foreground mt-1">
              {new Date(clip.start_time).toLocaleString('pt-BR')} - {new Date(clip.end_time).toLocaleString('pt-BR')}
            </p>
          </div>
          <Button variant="outline" onClick={onClose}>
            <X className="w-4 h-4 mr-2" />
            Fechar
          </Button>
        </div>
      </div>
    </div>
  )
}

function CreateClipModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [cameraId, setCameraId] = useState('')
  const [clipName, setClipName] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')

  const { data: cameras } = useQuery<Camera[]>({
    queryKey: ['cameras'],
    queryFn: async () => {
      const { cameraService } = await import('@/services/api')
      return cameraService.list()
    },
  })

  const createMutation = useMutation({
    mutationFn: clipService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clips'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!cameraId || !clipName || !startTime || !endTime) return

    createMutation.mutate({
      camera_id: parseInt(cameraId),
      name: clipName,
      start_time: startTime,
      end_time: endTime,
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/80" />
      <Card className="relative w-full max-w-md" onClick={(e) => e.stopPropagation()}>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Criar Clip</h2>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label>Câmera</Label>
              <select
                value={cameraId}
                onChange={(e) => setCameraId(e.target.value)}
                className="w-full mt-1 px-3 py-2 border rounded-md"
                required
              >
                <option value="">Selecione uma câmera</option>
                {cameras?.map((cam) => (
                  <option key={cam.id} value={cam.id}>
                    {cam.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Label>Nome do Clip</Label>
              <Input
                value={clipName}
                onChange={(e) => setClipName(e.target.value)}
                placeholder="Ex: Incidente 15:30"
                required
              />
            </div>

            <div>
              <Label>Início</Label>
              <Input
                type="datetime-local"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                required
              />
            </div>

            <div>
              <Label>Fim</Label>
              <Input
                type="datetime-local"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                required
              />
            </div>

            <div className="flex gap-2 pt-4">
              <Button type="button" variant="outline" onClick={onClose} className="flex-1">
                Cancelar
              </Button>
              <Button type="submit" disabled={createMutation.isPending} className="flex-1">
                {createMutation.isPending ? 'Criando...' : 'Criar Clip'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
