import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Video, Camera, ChevronLeft } from 'lucide-react'
import { Button, Card, CardContent } from '@/components/ui'
import { cameraService } from '@/services/api'
import { PlaybackPlayer } from '@/components/cameras/PlaybackPlayer'

export function RecordingsPage() {
  const [selectedCamera, setSelectedCamera] = useState<{ id: number; name: string } | null>(null)

  const { data: cameras, isLoading } = useQuery({
    queryKey: ['cameras'],
    queryFn: cameraService.list,
  })

  if (selectedCamera) {
    return (
      <div className="space-y-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setSelectedCamera(null)}
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Voltar
        </Button>
        <PlaybackPlayer
          cameraId={selectedCamera.id}
          cameraName={selectedCamera.name}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Gravações</h1>
        <p className="text-muted-foreground">
          Acesse gravações locais das câmeras
        </p>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">Carregando...</p>
      ) : cameras && cameras.length > 0 ? (
        <div className="space-y-2">
          {cameras.map((cam) => (
            <Card
              key={cam.id}
              className="hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => setSelectedCamera({ id: cam.id, name: cam.name })}
            >
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Video className="w-5 h-5 text-muted-foreground" />
                  <div>
                    <h3 className="font-medium">{cam.name}</h3>
                    {cam.location && (
                      <p className="text-sm text-muted-foreground">{cam.location}</p>
                    )}
                  </div>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  cam.status === 'online'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  {cam.status === 'online' ? 'Online' : 'Offline'}
                </span>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Camera className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">Nenhuma câmera cadastrada</p>
        </div>
      )}
    </div>
  )
}
