import { useState } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { Save, Plus, Trash2, Settings, Edit } from 'lucide-react'
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui'
import { ROIEditor } from './ROIEditor'
import { aiService, cameraService, streamingService } from '@/services/api'
import type { Camera, ROIArea, VirtualLine, ZoneTrigger } from '@/types'

interface DetectionConfigProps {
  camera: Camera
  onClose: () => void
}

export function DetectionConfig({ camera, onClose }: DetectionConfigProps) {
  const queryClient = useQueryClient()
  const [retentionDays, setRetentionDays] = useState(camera.recording_retention_days || 30)

  const updateMutation = useMutation({
    mutationFn: (config: any) => cameraService.updateDetectionConfig(camera.id, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
      onClose()
    },
  })

  const handleSave = () => {
    updateMutation.mutate({
      recording_retention_days: retentionDays,
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto bg-card rounded-xl">
        <div className="sticky top-0 bg-card border-b p-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Configurações de Detecção - {camera.name}
            </h2>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={onClose}>
              Cancelar
            </Button>
            <Button onClick={handleSave} disabled={updateMutation.isPending}>
              <Save className="w-4 h-4 mr-2" />
              Salvar
            </Button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Inteligência Artificial</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm bg-blue-50 p-3 rounded">
                <div className="text-blue-800 font-medium mb-1">✓ IA Sempre Ativa</div>
                <div className="text-blue-700 text-xs">
                  Câmeras RTSP/RTMP têm detecção automática de placas habilitada por padrão
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Configurações de Gravação</CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <label className="text-sm font-medium">Retenção de Gravações</label>
                <select 
                  value={retentionDays.toString()} 
                  onChange={(e) => setRetentionDays(parseInt(e.target.value))}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring mt-2"
                >
                  <option value="7">7 dias</option>
                  <option value="15">15 dias</option>
                  <option value="30">30 dias</option>
                </select>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}