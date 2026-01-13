import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Loader2 } from 'lucide-react'
import { Button, Card, CardHeader, CardTitle, CardContent } from '@/components/ui'
import { cameraService } from '@/services/api'
import type { Camera } from '@/types'

interface DetectionConfigProps {
  camera: Camera
  onClose: () => void
}

export function DetectionConfig({ camera, onClose }: DetectionConfigProps) {
  const queryClient = useQueryClient()

  const updateMutation = useMutation({
    mutationFn: (data: any) =>
      cameraService.update(camera.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cameras'] })
      onClose()
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Apenas atualiza outras configs, IA é ativada automaticamente no backend
    updateMutation.mutate({})
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <Card className="relative w-full max-w-md animate-slide-in">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Configurar Detecção - {camera.name}</CardTitle>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-sm">
                <p className="font-medium text-blue-900 dark:text-blue-100 mb-1">
                  IA ativada automaticamente
                </p>
                <p className="text-blue-700 dark:text-blue-300">
                  Câmeras RTSP têm detecção de placas (LPR) ativada automaticamente usando YOLO + OCR + Tracking + Voting.
                </p>
              </div>
            </div>

            {updateMutation.isError && (
              <div className="p-3 rounded-lg bg-destructive/10 text-sm text-destructive">
                Erro ao atualizar configuração. Tente novamente.
              </div>
            )}

            <div className="flex gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                className="flex-1"
                onClick={onClose}
              >
                Fechar
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
