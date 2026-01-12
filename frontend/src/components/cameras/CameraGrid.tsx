import { Grid2X2, Grid3X3, Square, LayoutGrid, RefreshCw, AlertTriangle } from 'lucide-react'
import type { Camera } from '@/types'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui'
import { CameraCard } from './CameraCard'
import { useCameraStore } from '@/store/cameraStore'
import { useState, useEffect } from 'react'
import { cameraService } from '@/services/api'

interface CameraGridProps {
  cameras: Camera[]
  onCameraClick?: (camera: Camera) => void
  onCameraDelete?: (camera: Camera) => void
}

export function CameraGrid({ cameras, onCameraClick, onCameraDelete }: CameraGridProps) {
  const { gridLayout, setGridLayout } = useCameraStore()
  const [offlineCameras, setOfflineCameras] = useState<Set<number>>(new Set())
  const [mediaMtxDown, setMediaMtxDown] = useState(false)
  const [lastFrames, setLastFrames] = useState<Record<number, string>>({})

  // Check camera and MediaMTX status
  useEffect(() => {
    const checkStatus = async () => {
      const offline = new Set<number>()
      let mtxDown = false

      for (const camera of cameras) {
        try {
          await cameraService.getStream(camera.id)
        } catch (error: any) {
          if (error.response?.status === 503) {
            mtxDown = true
          } else {
            offline.add(camera.id)
          }
        }
      }

      setOfflineCameras(offline)
      setMediaMtxDown(mtxDown)
    }

    checkStatus()
    const interval = setInterval(checkStatus, 30000)
    return () => clearInterval(interval)
  }, [cameras])

  const handleRetry = async (cameraId: number) => {
    try {
      await cameraService.getStream(cameraId)
      setOfflineCameras(prev => {
        const next = new Set(prev)
        next.delete(cameraId)
        return next
      })
    } catch (error) {
      console.error('Retry failed:', error)
    }
  }

  const layouts = [
    { value: 1 as const, icon: Square, label: '1x1' },
    { value: 4 as const, icon: Grid2X2, label: '2x2' },
    { value: 9 as const, icon: Grid3X3, label: '3x3' },
    { value: 16 as const, icon: LayoutGrid, label: '4x4' },
  ]

  const getGridClass = () => {
    switch (gridLayout) {
      case 1: return 'grid-cols-1'
      case 4: return 'grid-cols-1 sm:grid-cols-2'
      case 9: return 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3'
      case 16: return 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4'
      default: return 'grid-cols-2'
    }
  }

  return (
    <div className="space-y-4">
      {/* Layout controls */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {cameras.length} câmera{cameras.length !== 1 ? 's' : ''}
        </p>
        
        <div className="flex items-center gap-1 bg-secondary rounded-lg p-1">
          {layouts.map((layout) => (
            <Button
              key={layout.value}
              variant={gridLayout === layout.value ? 'default' : 'ghost'}
              size="sm"
              className={cn(
                "h-8 w-8 p-0",
                gridLayout === layout.value && "shadow-sm"
              )}
              onClick={() => setGridLayout(layout.value)}
              title={layout.label}
            >
              <layout.icon className="w-4 h-4" />
            </Button>
          ))}
        </div>
      </div>

      {/* Grid */}
      {mediaMtxDown ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <AlertTriangle className="w-16 h-16 text-destructive mb-4" />
          <h3 className="text-lg font-medium mb-1">Servidor de streaming indisponível</h3>
          <p className="text-sm text-muted-foreground mb-4">
            O MediaMTX está offline. Aguarde a reconexão automática.
          </p>
        </div>
      ) : cameras.length > 0 ? (
        offlineCameras.size === cameras.length ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <AlertTriangle className="w-16 h-16 text-yellow-500 mb-4" />
            <h3 className="text-lg font-medium mb-1">Sistema em manutenção</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Todas as câmeras estão offline. Tentando reconectar...
            </p>
          </div>
        ) : (
          <div className={cn("grid gap-4", getGridClass())}>
            {cameras.slice(0, gridLayout).map((camera) => (
              <div key={camera.id} className="relative">
                <CameraCard
                  camera={camera}
                  onClick={() => onCameraClick?.(camera)}
                  onDelete={() => onCameraDelete?.(camera)}
                  compact={gridLayout > 4}
                />
                {offlineCameras.has(camera.id) && (
                  <div className="absolute inset-0 bg-black/80 rounded-lg flex flex-col items-center justify-center gap-3">
                    {lastFrames[camera.id] && (
                      <img 
                        src={lastFrames[camera.id]} 
                        alt="Last frame" 
                        className="absolute inset-0 w-full h-full object-cover opacity-30 rounded-lg"
                      />
                    )}
                    <div className="relative z-10 text-center">
                      <p className="text-sm text-yellow-500 mb-2">Reconectando...</p>
                      <Button 
                        size="sm" 
                        variant="secondary"
                        onClick={() => handleRetry(camera.id)}
                      >
                        <RefreshCw className="w-3 h-3 mr-1" />
                        Tentar novamente
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )
      ) : (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center mb-4">
            <Grid2X2 className="w-8 h-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium mb-1">Nenhuma câmera</h3>
          <p className="text-sm text-muted-foreground">
            Adicione uma câmera para começar
          </p>
        </div>
      )}

      {/* Pagination hint */}
      {cameras.length > gridLayout && (
        <p className="text-center text-sm text-muted-foreground">
          Mostrando {gridLayout} de {cameras.length} câmeras
        </p>
      )}
    </div>
  )
}
