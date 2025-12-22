import { Grid2X2, Grid3X3, Square, LayoutGrid } from 'lucide-react'
import type { Camera } from '@/types'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui'
import { CameraCard } from './CameraCard'
import { useCameraStore } from '@/store/cameraStore'

interface CameraGridProps {
  cameras: Camera[]
  onCameraClick?: (camera: Camera) => void
  onCameraDelete?: (camera: Camera) => void
}

export function CameraGrid({ cameras, onCameraClick, onCameraDelete }: CameraGridProps) {
  const { gridLayout, setGridLayout } = useCameraStore()

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
      {cameras.length > 0 ? (
        <div className={cn("grid gap-4", getGridClass())}>
          {cameras.slice(0, gridLayout).map((camera) => (
            <CameraCard
              key={camera.id}
              camera={camera}
              onClick={() => onCameraClick?.(camera)}
              onDelete={() => onCameraDelete?.(camera)}
              compact={gridLayout > 4}
            />
          ))}
        </div>
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
