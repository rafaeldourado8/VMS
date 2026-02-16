import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, X } from 'lucide-react'
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui'
import { cameraService } from '@/services/api'
import type { Camera } from '@/types'

const RETENTION_PLANS = [
  { value: 7, label: '7 dias', description: 'Retenção curta - ideal para monitoramento básico' },
  { value: 15, label: '15 dias', description: 'Retenção média - balanceamento entre espaço e histórico' },
  { value: 30, label: '30 dias', description: 'Retenção longa - máximo histórico disponível' },
]

interface CameraConfigProps {
  camera: Camera
  onClose: () => void
}

export function CameraConfig({ camera, onClose }: CameraConfigProps) {
  const queryClient = useQueryClient()
  
  const [name, setName] = useState(camera.name)
  const [location, setLocation] = useState(camera.location || '')
  const [streamUrl, setStreamUrl] = useState(camera.stream_url)
  const [retentionDays, setRetentionDays] = useState(camera.recording_retention_days || 7)
  const [onvifHost, setOnvifHost] = useState(camera.onvif_host || '')
  const [onvifPort, setOnvifPort] = useState(camera.onvif_port || 80)
  const [onvifUsername, setOnvifUsername] = useState(camera.onvif_username || '')
  const [onvifPassword, setOnvifPassword] = useState('')

  const updateMutation = useMutation({
    mutationFn: () => cameraService.update(camera.id, {
      name,
      location,
      stream_url: streamUrl,
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
    },
  })

  const updateConfigMutation = useMutation({
    mutationFn: () => cameraService.updateDetectionConfig(camera.id, {
      recording_retention_days: retentionDays,
      onvif_host: onvifHost,
      onvif_port: onvifPort,
      onvif_username: onvifUsername,
      ...(onvifPassword && { onvif_password: onvifPassword }),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
    },
  })

  const handleSave = async () => {
    await updateMutation.mutateAsync()
    await updateConfigMutation.mutateAsync()
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-card rounded-xl">
        <div className="sticky top-0 bg-card border-b p-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            Configurações - {camera.name}
          </h2>
          <div className="flex gap-2">
            <Button variant="outline" onClick={onClose}>
              <X className="w-4 h-4 mr-2" />
              Cancelar
            </Button>
            <Button 
              onClick={handleSave} 
              disabled={updateMutation.isPending || updateConfigMutation.isPending}
            >
              <Save className="w-4 h-4 mr-2" />
              Salvar
            </Button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Informações Básicas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Nome da Câmera</label>
                <Input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Câmera Entrada"
                  className="mt-2"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium">Localização</label>
                <Input
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Portaria Principal"
                  className="mt-2"
                />
              </div>

              <div>
                <label className="text-sm font-medium">URL do Stream RTSP</label>
                <Input
                  value={streamUrl}
                  onChange={(e) => setStreamUrl(e.target.value)}
                  placeholder="rtsp://admin:pass@192.168.1.100:554/stream"
                  className="mt-2"
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Plano de Gravação</CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <label className="text-sm font-medium">Retenção de Gravações *</label>
                <select 
                  value={retentionDays}
                  onChange={(e) => setRetentionDays(parseInt(e.target.value))}
                  className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm mt-2"
                >
                  {RETENTION_PLANS.map(plan => (
                    <option key={plan.value} value={plan.value}>
                      {plan.label}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-muted-foreground mt-2">
                  {RETENTION_PLANS.find(p => p.value === retentionDays)?.description}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Playback ONVIF (Opcional)</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-sm text-muted-foreground">
                Configure para acessar gravações direto do storage da câmera via ONVIF
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">IP da Câmera</label>
                  <Input
                    placeholder="192.168.1.100"
                    value={onvifHost}
                    onChange={(e) => setOnvifHost(e.target.value)}
                    className="mt-2"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Porta ONVIF</label>
                  <Input
                    type="number"
                    placeholder="80"
                    value={onvifPort}
                    onChange={(e) => setOnvifPort(parseInt(e.target.value) || 80)}
                    className="mt-2"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Usuário ONVIF</label>
                  <Input
                    placeholder="admin"
                    value={onvifUsername}
                    onChange={(e) => setOnvifUsername(e.target.value)}
                    className="mt-2"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Senha ONVIF</label>
                  <Input
                    type="password"
                    placeholder="Deixe vazio para não alterar"
                    value={onvifPassword}
                    onChange={(e) => setOnvifPassword(e.target.value)}
                    className="mt-2"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}