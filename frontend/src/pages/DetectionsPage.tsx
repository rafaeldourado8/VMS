import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Filter, Car, Calendar, Camera, ChevronLeft, ChevronRight, X } from 'lucide-react'
import {
  Button,
  Input,
  Card,
  CardContent,
  Badge,
  Skeleton,
} from '@/components/ui'
import { detectionService, cameraService } from '@/services/api'
import { formatDate, getVehicleTypeLabel } from '@/lib/utils'
import type { Detection } from '@/types'

export function DetectionsPage() {
  const [search, setSearch] = useState('')
  const [cameraFilter, setCameraFilter] = useState<number | undefined>()
  const [page, setPage] = useState(1)
  const [selectedDetection, setSelectedDetection] = useState<Detection | null>(null)

  const { data: detectionsData, isLoading } = useQuery({
    queryKey: ['detections', { plate: search, camera_id: cameraFilter, page }],
    queryFn: () =>
      detectionService.list({
        plate: search || undefined,
        camera_id: cameraFilter,
        page,
      }),
  })

  const { data: cameras } = useQuery({
    queryKey: ['cameras'],
    queryFn: cameraService.list,
  })

  const detections = detectionsData?.results ?? []
  const totalPages = Math.ceil((detectionsData?.count ?? 0) / 20)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Detecções</h1>
        <p className="text-muted-foreground">
          Histórico de veículos e placas detectadas
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por placa..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
              className="pl-10"
            />
          </div>

          <div className="flex gap-2">
            <select
              className="h-9 px-3 rounded-md border border-input bg-transparent text-sm focus:outline-none focus:ring-1 focus:ring-ring"
              value={cameraFilter ?? ''}
              onChange={(e) => {
                setCameraFilter(e.target.value ? Number(e.target.value) : undefined)
                setPage(1)
              }}
            >
              <option value="">Todas as câmeras</option>
              {cameras?.map((cam) => (
                <option key={cam.id} value={cam.id}>
                  {cam.name}
                </option>
              ))}
            </select>

            {(search || cameraFilter) && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setSearch('')
                  setCameraFilter(undefined)
                  setPage(1)
                }}
              >
                <X className="w-4 h-4 mr-1" />
                Limpar
              </Button>
            )}
          </div>
        </div>

      {/* Stats */}
      <div className="flex items-center gap-4 text-sm text-muted-foreground">
        <span>{detectionsData?.count ?? 0} detecções encontradas</span>
        {search && <span>• Filtro: "{search}"</span>}
      </div>

      {/* Table */}
      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="divide-y divide-border">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="p-4">
                  <Skeleton className="h-16 w-full" />
                </div>
              ))}
            </div>
          ) : detections.length > 0 ? (
            <div className="divide-y divide-border">
              {detections.map((detection) => (
                <DetectionRow
                  key={detection.id}
                  detection={detection}
                  onClick={() => setSelectedDetection(detection)}
                />
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-16">
              <Car className="w-12 h-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium">Nenhuma detecção</h3>
              <p className="text-sm text-muted-foreground">
                {search
                  ? 'Nenhum resultado para sua busca'
                  : 'Aguardando detecções...'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Página {page} de {totalPages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Anterior
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page === totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Próxima
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      )}

      {/* Detection Detail Modal */}
      {selectedDetection && (
        <DetectionDetailModal
          detection={selectedDetection}
          onClose={() => setSelectedDetection(null)}
        />
      )}
    </div>
  )
}

// Detection Row Component
function DetectionRow({
  detection,
  onClick,
}: {
  detection: Detection
  onClick: () => void
}) {
  const vehicleIcons: Record<string, string> = {
    car: '🚗',
    motorcycle: '🏍️',
    truck: '🚚',
    bus: '🚌',
    unknown: '🚙',
  }

  return (
    <div
      className="flex items-center gap-4 p-4 hover:bg-secondary/50 cursor-pointer transition-colors"
      onClick={onClick}
    >
      {/* Thumbnail */}
      <div className="w-24 h-16 rounded-lg bg-secondary flex items-center justify-center overflow-hidden flex-shrink-0">
        {detection.image_url ? (
          <img
            src={detection.image_url}
            alt="Captura"
            className="w-full h-full object-cover"
          />
        ) : (
          <Car className="w-6 h-6 text-muted-foreground" />
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-lg">
            {vehicleIcons[detection.vehicle_type] || vehicleIcons.unknown}
          </span>
          {detection.plate ? (
            <span className="font-mono font-bold text-lg tracking-wider">
              {detection.plate}
            </span>
          ) : (
            <span className="text-muted-foreground">Sem placa</span>
          )}
          {detection.confidence && (
            <Badge variant="secondary" className="text-xs">
              {Math.round(detection.confidence * 100)}%
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Camera className="w-3.5 h-3.5" />
            {detection.camera_name}
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5" />
            {formatDate(detection.timestamp)}
          </span>
        </div>
      </div>

      {/* Type Badge */}
      <Badge variant="outline" className="flex-shrink-0">
        {getVehicleTypeLabel(detection.vehicle_type)}
      </Badge>
    </div>
  )
}

// Detection Detail Modal
function DetectionDetailModal({
  detection,
  onClose,
}: {
  detection: Detection
  onClose: () => void
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/80" onClick={onClose} />
      <Card className="relative w-full max-w-2xl animate-slide-in">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-lg font-semibold">Detalhes da Detecção</h2>
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="w-5 h-5" />
          </Button>
        </div>

        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Image */}
            <div className="aspect-video rounded-lg bg-secondary flex items-center justify-center overflow-hidden">
              {detection.image_url ? (
                <img
                  src={detection.image_url}
                  alt="Captura do veículo"
                  className="w-full h-full object-contain"
                />
              ) : (
                <div className="text-center">
                  <Car className="w-12 h-12 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">
                    Imagem não disponível
                  </p>
                </div>
              )}
            </div>

            {/* Details */}
            <div className="space-y-4">
              {/* Plate */}
              <div>
                <p className="text-sm text-muted-foreground mb-1">Placa</p>
                {detection.plate ? (
                  <p className="text-3xl font-mono font-bold tracking-widest">
                    {detection.plate}
                  </p>
                ) : (
                  <p className="text-lg text-muted-foreground">Não identificada</p>
                )}
              </div>

              {/* Other info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Tipo</p>
                  <p className="font-medium">
                    {getVehicleTypeLabel(detection.vehicle_type)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Confiança</p>
                  <p className="font-medium">
                    {detection.confidence
                      ? `${Math.round(detection.confidence * 100)}%`
                      : 'N/A'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Câmera</p>
                  <p className="font-medium">{detection.camera_name}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Data/Hora</p>
                  <p className="font-medium">{formatDate(detection.timestamp)}</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4">
                <Button variant="outline" className="flex-1">
                  <Filter className="w-4 h-4 mr-2" />
                  Buscar placa
                </Button>
                {detection.video_url && (
                  <Button variant="outline" className="flex-1">
                    Ver vídeo
                  </Button>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
