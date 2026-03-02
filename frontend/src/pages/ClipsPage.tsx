import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, Play, Download, Trash2, Calendar, Clock, Scissors, X, Edit2 } from 'lucide-react'
import {
  Button,
  Input,
  Card,
  CardContent,
  Skeleton,
  Label,
  ConfirmDialog,
  PromptDialog,
  Dialog,
} from '@/components/ui'
import { clipService, recordingService } from '@/services/api'
import type { Clip, Camera } from '@/types'

export function ClipsPage() {
  const queryClient = useQueryClient()
  const [search, setSearch] = useState('')
  const [selectedClip, setSelectedClip] = useState<Clip | null>(null)
  const [showCreateClip, setShowCreateClip] = useState(false)
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; clip: Clip | null }>({ open: false, clip: null })
  const [renameDialog, setRenameDialog] = useState<{ open: boolean; clip: Clip | null }>({ open: false, clip: null })

  const { data: clips, isLoading } = useQuery({
    queryKey: ['clips'],
    queryFn: clipService.list,
    refetchInterval: 5000, // Atualiza a cada 5 segundos
  })

  const renameMutation = useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) => clipService.rename(id, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clips'] })
    },
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

  const handleRename = (clip: Clip) => {
    setRenameDialog({ open: true, clip })
  }

  const handleDelete = (clip: Clip) => {
    setDeleteDialog({ open: true, clip })
  }

  const handleDownload = async (clip: Clip) => {
    if (clip.status !== 'completed') {
      alert('Aguarde o processamento do clip terminar')
      return
    }
    const url = `/api/clips-service/${clip.id}/download`
    window.open(url, '_blank')
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Meus Clips</h1>
        <p className="text-muted-foreground">Clips salvos das gravações</p>
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
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
      ) : filteredClips.length === 0 ? (
        <Card className="p-12 text-center">
          <Scissors className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">Nenhum clip encontrado</h3>
          <p className="text-muted-foreground">Crie clips na timeline das câmeras</p>
        </Card>
      ) : (
        <div className="space-y-2">
          {filteredClips.map((clip) => (
            <Card key={clip.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="flex gap-4 p-4">
                <div className="w-40 h-24 bg-black rounded flex-shrink-0 relative group cursor-pointer"
                     onClick={() => setSelectedClip(clip)}>
                  {clip.status === 'completed' ? (
                    <>
                      <video 
                        src={`/api/clips-service/${clip.id}/download#t=0.1`}
                        className="w-full h-full object-cover"
                        muted
                        preload="metadata"
                      />
                      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <Play className="w-10 h-10 text-white" />
                      </div>
                    </>
                  ) : (
                    <div className="absolute inset-0 flex items-center justify-center bg-zinc-900">
                      <Play className="w-8 h-8 text-white/60" />
                    </div>
                  )}
                  <div className="absolute bottom-1 right-1 bg-black/80 text-white text-xs px-1.5 py-0.5 rounded">
                    {formatDuration(clip.duration_seconds)}
                  </div>
                </div>
                
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold truncate">{clip.name}</h3>
                  <p className="text-sm text-muted-foreground truncate">{clip.camera_name || 'Câmera removida'}</p>
                  
                  {clip.status && clip.status !== 'completed' && (
                    <div className="mt-2">
                      <span className={`text-xs px-2 py-1 rounded ${
                        clip.status === 'processing' ? 'bg-blue-500/20 text-blue-400' :
                        clip.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-red-500/20 text-red-400'
                      }`}>
                        {clip.status === 'processing' ? '⏳ Processando...' :
                         clip.status === 'pending' ? '⏳ Aguardando...' : '❌ Falhou'}
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
                </div>

                <div className="flex gap-2 items-center">
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleRename(clip)}
                    title="Renomear"
                  >
                    <Edit2 className="w-4 h-4" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => setSelectedClip(clip)}
                    disabled={clip.status === 'failed'}
                  >
                    <Play className="w-4 h-4" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleDownload(clip)}
                    disabled={clip.status !== 'completed'}
                    title={clip.status !== 'completed' ? 'Aguarde o processamento' : 'Download'}
                  >
                    <Download className="w-4 h-4" />
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleDelete(clip)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
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

      <ConfirmDialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, clip: null })}
        onConfirm={() => deleteDialog.clip && deleteMutation.mutate(deleteDialog.clip.id)}
        title="Remover Clip"
        message={`Tem certeza que deseja remover "${deleteDialog.clip?.name}"?`}
        confirmText="Remover"
        variant="danger"
      />

      <PromptDialog
        open={renameDialog.open}
        onClose={() => setRenameDialog({ open: false, clip: null })}
        onConfirm={(name) => renameDialog.clip && renameMutation.mutate({ id: renameDialog.clip.id, name })}
        title="Renomear Clip"
        placeholder="Nome do clip"
        defaultValue={renameDialog.clip?.name || ''}
        confirmText="Renomear"
      />
    </div>
  )
}

function ClipPlayerModal({ clip, onClose }: { clip: Clip; onClose: () => void }) {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // Fechar com ESC
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [onClose])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm" onClick={onClose}>
      <div className="relative w-full max-w-6xl mx-4" onClick={(e) => e.stopPropagation()}>
        {/* Botão Fechar */}
        <button
          onClick={onClose}
          className="absolute -top-12 right-0 text-white hover:text-gray-300 transition-colors flex items-center gap-2 text-sm"
        >
          <span className="hidden sm:inline">Pressione ESC para fechar</span>
          <X className="w-6 h-6" />
        </button>

        {/* Player */}
        <div className="bg-background rounded-lg shadow-2xl overflow-hidden">
          <div className="aspect-video bg-black">
            <video
              src={`/api/clips-service/${clip.id}/download`}
              controls
              controlsList="nodownload"
              autoPlay
              className="w-full h-full"
            />
          </div>
          
          {/* Info Bar */}
          <div className="p-4 border-t border-border bg-card">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <h2 className="text-lg font-semibold truncate">{clip.name}</h2>
                <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground flex-wrap">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-4 h-4" />
                    <span>{new Date(clip.start_time).toLocaleDateString('pt-BR')}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-4 h-4" />
                    <span>{new Date(clip.start_time).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })} - {new Date(clip.end_time).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                  <div className="px-2 py-0.5 bg-primary/10 text-primary rounded text-xs font-medium">
                    {formatDuration(clip.duration_seconds)}
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  📹 {clip.camera_name || 'Câmera removida'}
                </p>
              </div>
              
              <Button
                size="sm"
                variant="outline"
                onClick={() => window.open(`/api/clips-service/${clip.id}/download`, '_blank')}
                className="flex-shrink-0"
              >
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
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
    <Dialog open={true} onClose={onClose} title="Criar Clip" maxWidth="md">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label>Câmera</Label>
          <select
            value={cameraId}
            onChange={(e) => setCameraId(e.target.value)}
            className="w-full mt-1 px-3 py-2 border border-border rounded-md bg-background"
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
    </Dialog>
  )
}
