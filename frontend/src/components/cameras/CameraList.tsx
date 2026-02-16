import { Eye, Settings, Trash2 } from 'lucide-react'
import { Button, Card, CardContent } from '@/components/ui'
import { StreamThumbnail } from './StreamThumbnail'
import type { Camera } from '@/types'

interface CameraListProps {
  cameras: Camera[]
  onCameraView: (camera: Camera) => void
  onCameraConfig: (camera: Camera) => void
  onCameraDelete: (camera: Camera) => void
}

export function CameraList({ cameras, onCameraView, onCameraConfig, onCameraDelete }: CameraListProps) {
  return (
    <div className="space-y-3">
      {cameras.map((camera) => (
        <Card key={camera.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <StreamThumbnail
                  cameraId={camera.id}
                  cameraName={camera.name}
                  cameraStatus={camera.status}
                  className="w-20 h-12 flex-shrink-0"
                  onClick={() => onCameraView(camera)}
                  showStatus={true}
                />
                <div>
                  <h3 className="font-semibold">{camera.name}</h3>
                  <p className="text-sm text-muted-foreground">{camera.location || 'Sem localização'}</p>
                  <div className="flex items-center gap-4 mt-1">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      camera.status === 'online' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {camera.status === 'online' ? 'Online' : 'Offline'}
                    </span>
                    <span className="text-xs text-muted-foreground">ID: {camera.id}</span>
                    <span className="text-xs text-muted-foreground">{camera.recording_retention_days}d</span>
                  </div>
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={() => onCameraView(camera)}>
                  <Eye className="w-4 h-4 mr-2" />
                  Visualizar
                </Button>
                <Button size="sm" variant="outline" onClick={() => onCameraConfig(camera)}>
                  <Settings className="w-4 h-4 mr-2" />
                  Configurar
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => onCameraDelete(camera)}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Remover
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
      
      {cameras.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Nenhuma câmera encontrada</p>
        </div>
      )}
    </div>
  )
}
