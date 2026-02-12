import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Loader2 } from 'lucide-react'
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@/components/ui'
import { cameraService, streamingService } from '@/services/api'
import type { CameraCreateRequest } from '@/types'

interface AddCameraModalProps {
  onClose: () => void
}

export function AddCameraModal({ onClose }: AddCameraModalProps) {
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
            <Button onClick={() => setMode('easy')} className="w-full h-20 text-lg" variant="outline">
              <div>
                <div className="font-semibold">Modo Fácil</div>
                <div className="text-xs text-muted-foreground">Configuração guiada</div>
              </div>
            </Button>
            <Button onClick={() => setMode('advanced')} className="w-full h-20 text-lg" variant="outline">
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
        <Card className="relative w-full max-w-md animate-slide-in max-h-[90vh] overflow-y-auto">
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

              <div className="space-y-2">
                <label className="text-sm font-medium">Plano de Gravação</label>
                <select
                  className="w-full px-3 py-2 border rounded-md"
                  value={formData.recording_retention_days || 30}
                  onChange={(e) => setFormData(f => ({ ...f, recording_retention_days: parseInt(e.target.value) }))}
                >
                  <option value={7}>7 dias (cíclico)</option>
                  <option value={15}>15 dias (cíclico)</option>
                  <option value={30}>30 dias (cíclico)</option>
                </select>
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

            <div className="space-y-2">
              <label className="text-sm font-medium">Plano de Gravação</label>
              <select
                className="w-full px-3 py-2 border rounded-md"
                value={formData.recording_retention_days || 30}
                onChange={(e) => setFormData(f => ({ ...f, recording_retention_days: parseInt(e.target.value) }))}
              >
                <option value={7}>7 dias (cíclico)</option>
                <option value={15}>15 dias (cíclico)</option>
                <option value={30}>30 dias (cíclico)</option>
              </select>
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
