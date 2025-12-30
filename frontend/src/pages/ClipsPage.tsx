import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Play, Download, Trash2, Calendar, Clock } from 'lucide-react'
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
import { clipService } from '@/services/api'
import type { Clip } from '@/types'

export function ClipsPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [selectedClip, setSelectedClip] = useState<Clip | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)

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
    clip.name.toLowerCase().includes(search.toLowerCase()) ||
    clip.camera.name.toLowerCase().includes(search.toLowerCase())
  )

  const handleDelete = (clip: Clip) => {
    if (confirm(`Remover clip "${clip.name}"?`)) {
      deleteMutation.mutate(clip.id)
    }
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Meus Clips</h1>
          <p className="text-muted-foreground">Gerencie seus clips de vídeo salvos</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Criar Clip
        </Button>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Buscar clips..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Clips Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="aspect-video rounded-xl" />
          ))}
        </div>
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
                <p className="text-sm text-muted-foreground truncate">{clip.camera.name}</p>
                
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
                  >
                    <Play className="w-3 h-3 mr-1" />
                    Assistir
                  </Button>
                  <Button size="sm" variant="outline">
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

      {/* Clip Player Modal */}
      {selectedClip && (
        <ClipPlayerModal
          clip={selectedClip}
          onClose={() => setSelectedClip(null)}
        />
      )}

      {/* Create Clip Modal */}
      {showCreateModal && (
        <CreateClipModal onClose={() => setShowCreateModal(false)} />
      )}
    </div>
  )
}

// Clip Player Modal
function ClipPlayerModal({ clip, onClose }: { clip: Clip; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <div className="relative w-full max-w-4xl bg-card rounded-xl overflow-hidden">
        <div className="aspect-video bg-black">
          <VideoPlayer
            src={clip.file_path}
            autoPlay
            muted={false}
            className="h-full"
          />
        </div>
        <div className="p-4">
          <h2 className="text-lg font-semibold">{clip.name}</h2>
          <p className="text-sm text-muted-foreground">{clip.camera.name}</p>
        </div>
      </div>
    </div>
  )
}

// Create Clip Modal (placeholder)
function CreateClipModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <Card className="relative w-full max-w-md">
        <CardHeader>
          <CardTitle>Criar Clip</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Funcionalidade em desenvolvimento. 
            Use o player de câmera para criar clips.
          </p>
          <Button onClick={onClose} className="w-full mt-4">
            Fechar
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}