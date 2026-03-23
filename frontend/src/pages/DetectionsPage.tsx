import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Car, Calendar, Camera, ChevronLeft, ChevronRight, X, Download, FileSpreadsheet } from 'lucide-react'
import {
  Button,
  Input,
  Card,
  CardContent,
  Badge,
  Skeleton,
} from '@/components/ui'
import { lprService, cameraService } from '@/services/api'
import { formatDate } from '@/lib/utils'
import type { LPRDetection, LPRStats } from '@/types'

function formatDateInput(date: Date): string {
  return date.toISOString().split('T')[0]
}

export function DetectionsPage() {
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  const [search, setSearch] = useState('')
  const [cameraFilter, setCameraFilter] = useState<number | undefined>()
  const [dateFrom, setDateFrom] = useState(formatDateInput(yesterday))
  const [dateTo, setDateTo] = useState(formatDateInput(today))
  const [page, setPage] = useState(1)
  const [selectedDetection, setSelectedDetection] = useState<LPRDetection | null>(null)

  const params = {
    plate_text: search || undefined,
    camera_id: cameraFilter,
    date_from: dateFrom ? `${dateFrom}T00:00:00` : undefined,
    date_to: dateTo ? `${dateTo}T23:59:59` : undefined,
    page,
    page_size: 50,
  }

  const { data: detectionsData, isLoading } = useQuery({
    queryKey: ['lpr-detections', params],
    queryFn: () => lprService.list(params),
  })

  const { data: stats } = useQuery({
    queryKey: ['lpr-stats', { date_from: params.date_from, date_to: params.date_to }],
    queryFn: () => lprService.stats({
      date_from: params.date_from,
      date_to: params.date_to,
    }),
  })

  const { data: cameras } = useQuery({
    queryKey: ['cameras'],
    queryFn: cameraService.list,
  })

  const detections = detectionsData?.results ?? []
  const totalCount = detectionsData?.count ?? 0
  const totalPages = Math.ceil(totalCount / 50)

  const exportCSV = () => {
    if (!detections.length) return
    const headers = ['Placa', 'Camera', 'Data', 'Confianca', 'Marca', 'Modelo', 'Cor', 'Tipo', 'Ano', 'Cidade']
    const rows = detections.map(d => [
      d.plate_text, d.camera_name, d.timestamp,
      `${(d.confidence * 100).toFixed(1)}%`,
      d.vehicle_brand, d.vehicle_model, d.vehicle_color,
      d.vehicle_type, d.vehicle_year || '', d.city,
    ])
    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `deteccoes_${dateFrom}_${dateTo}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Deteccoes LPR</h1>
        <p className="text-muted-foreground">Placas detectadas via push de cameras</p>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-end gap-3">
            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">De</label>
              <Input
                type="date"
                value={dateFrom}
                onChange={(e) => { setDateFrom(e.target.value); setPage(1) }}
                className="w-40"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">Ate</label>
              <Input
                type="date"
                value={dateTo}
                onChange={(e) => { setDateTo(e.target.value); setPage(1) }}
                className="w-40"
              />
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">Placa</label>
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar placa..."
                  value={search}
                  onChange={(e) => { setSearch(e.target.value.toUpperCase()); setPage(1) }}
                  className="pl-9 w-40"
                />
              </div>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">Camera</label>
              <select
                className="h-9 px-3 rounded-md border border-input bg-transparent text-sm focus:outline-none focus:ring-1 focus:ring-ring"
                value={cameraFilter ?? ''}
                onChange={(e) => { setCameraFilter(e.target.value ? Number(e.target.value) : undefined); setPage(1) }}
              >
                <option value="">Todas</option>
                {cameras?.map((cam) => (
                  <option key={cam.id} value={cam.id}>{cam.name}</option>
                ))}
              </select>
            </div>

            <div className="flex gap-2 ml-auto">
              <Button variant="outline" size="sm" onClick={exportCSV} disabled={!detections.length}>
                <FileSpreadsheet className="w-4 h-4 mr-1" />
                CSV
              </Button>
              {(search || cameraFilter) && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => { setSearch(''); setCameraFilter(undefined); setPage(1) }}
                >
                  <X className="w-4 h-4 mr-1" />
                  Limpar
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatsCard
          label="Registros"
          value={stats?.total ?? 0}
          sub="Mostrar todos"
        />
        <StatsCard
          label="Acima de 90%"
          value={stats?.above_90 ?? 0}
          sub={`${stats?.above_90_pct ?? 0}% do total`}
          variant="green"
        />
        <StatsCard
          label="Entre 75% e 90%"
          value={stats?.between_75_90 ?? 0}
          sub={`${stats?.between_75_90_pct ?? 0}% do total`}
          variant="yellow"
        />
        <StatsCard
          label="Abaixo de 75%"
          value={stats?.below_75 ?? 0}
          sub={`${stats?.below_75_pct ?? 0}% do total`}
          variant="red"
        />
      </div>

      {/* Count */}
      <p className="text-sm text-muted-foreground">{totalCount} deteccoes</p>

      {/* Table */}
      <Card>
        <CardContent className="p-0 overflow-x-auto">
          {isLoading ? (
            <div className="divide-y divide-border">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="p-4"><Skeleton className="h-14 w-full" /></div>
              ))}
            </div>
          ) : detections.length > 0 ? (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  <th className="text-left p-3 font-medium w-24"></th>
                  <th className="text-left p-3 font-medium">Placa</th>
                  <th className="text-left p-3 font-medium">Nome da camera</th>
                  <th className="text-left p-3 font-medium">Data</th>
                  <th className="text-left p-3 font-medium">Confianca</th>
                  <th className="text-left p-3 font-medium">Marca</th>
                  <th className="text-left p-3 font-medium">Modelo</th>
                  <th className="text-left p-3 font-medium">Cor</th>
                  <th className="text-left p-3 font-medium">Tipo</th>
                  <th className="text-left p-3 font-medium">Ano</th>
                  <th className="text-left p-3 font-medium">Cidade</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {detections.map((det) => (
                  <tr
                    key={det.id}
                    className="hover:bg-muted/20 cursor-pointer transition-colors"
                    onClick={() => setSelectedDetection(det)}
                  >
                    <td className="p-2">
                      <div className="w-20 h-12 rounded bg-muted flex items-center justify-center overflow-hidden">
                        {det.plate_image_url ? (
                          <img src={det.plate_image_url} alt={det.plate_text} className="w-full h-full object-cover" />
                        ) : det.full_frame_url ? (
                          <img src={det.full_frame_url} alt={det.plate_text} className="w-full h-full object-cover" />
                        ) : (
                          <Car className="w-5 h-5 text-muted-foreground" />
                        )}
                      </div>
                    </td>
                    <td className="p-3">
                      <span className="font-mono font-bold tracking-wider">
                        {det.plate_text || '-'}
                      </span>
                    </td>
                    <td className="p-3 text-muted-foreground">{det.camera_name}</td>
                    <td className="p-3 text-muted-foreground whitespace-nowrap">{formatDate(det.timestamp)}</td>
                    <td className="p-3">
                      <ConfidenceBadge value={det.confidence} />
                    </td>
                    <td className="p-3">{det.vehicle_brand || '-'}</td>
                    <td className="p-3 text-muted-foreground">{det.vehicle_model || '-'}</td>
                    <td className="p-3">{det.vehicle_color || '-'}</td>
                    <td className="p-3">{det.vehicle_type !== 'unknown' ? det.vehicle_type : '-'}</td>
                    <td className="p-3">{det.vehicle_year || '-'}</td>
                    <td className="p-3">{det.city || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="flex flex-col items-center justify-center py-16">
              <Car className="w-12 h-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium">Nenhuma deteccao</h3>
              <p className="text-sm text-muted-foreground">
                {search ? 'Nenhum resultado para sua busca' : 'Aguardando deteccoes das cameras...'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">Pagina {page} de {totalPages}</p>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>
              <ChevronLeft className="w-4 h-4 mr-1" /> Anterior
            </Button>
            <Button variant="outline" size="sm" disabled={page === totalPages} onClick={() => setPage(p => p + 1)}>
              Proxima <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      )}

      {/* Detail Modal */}
      {selectedDetection && (
        <DetectionDetailModal detection={selectedDetection} onClose={() => setSelectedDetection(null)} />
      )}
    </div>
  )
}

function StatsCard({ label, value, sub, variant }: {
  label: string; value: number; sub: string; variant?: 'green' | 'yellow' | 'red'
}) {
  const colors = {
    green: 'bg-green-50 border-green-200 text-green-800',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    red: 'bg-red-50 border-red-200 text-red-800',
  }
  return (
    <div className={`rounded-lg border p-3 ${variant ? colors[variant] : 'bg-card border-border'}`}>
      <p className="text-xs font-medium opacity-80">{label}</p>
      <p className="text-2xl font-bold">{value.toLocaleString()}</p>
      <p className="text-xs opacity-60">{sub}</p>
    </div>
  )
}

function ConfidenceBadge({ value }: { value: number }) {
  const pct = (value * 100).toFixed(1)
  let color = 'text-red-600'
  if (value >= 0.90) color = 'text-green-600'
  else if (value >= 0.75) color = 'text-yellow-600'
  return <span className={`font-medium ${color}`}>{pct}%</span>
}

function DetectionDetailModal({ detection, onClose }: { detection: LPRDetection; onClose: () => void }) {
  const [imageExpanded, setImageExpanded] = useState(false)
  const imageUrl = detection.full_frame_url || detection.plate_image_url

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="absolute inset-0 bg-black/80" onClick={onClose} />
        <Card className="relative w-full max-w-2xl animate-slide-in max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h2 className="text-lg font-semibold">Detalhes da Deteccao</h2>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-5 h-5" />
            </Button>
          </div>
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Image */}
              <div className="space-y-3">
                <div
                  className="aspect-video rounded-lg bg-muted flex items-center justify-center overflow-hidden cursor-pointer hover:ring-2 hover:ring-primary transition-all"
                  onClick={() => imageUrl && setImageExpanded(true)}
                >
                  {imageUrl ? (
                    <img src={imageUrl} alt="Frame" className="w-full h-full object-contain" />
                  ) : (
                    <Car className="w-12 h-12 text-muted-foreground" />
                  )}
                </div>
                {imageUrl && (
                  <p className="text-xs text-muted-foreground text-center">Clique na imagem para expandir</p>
                )}
                {detection.plate_image_url && detection.full_frame_url && (
                  <div className="w-32 h-16 rounded bg-muted overflow-hidden">
                    <img src={detection.plate_image_url} alt="Placa" className="w-full h-full object-cover" />
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Placa</p>
                  <p className="text-3xl font-mono font-bold tracking-widest">{detection.plate_text || 'N/A'}</p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <InfoField label="Camera" value={detection.camera_name} />
                  <InfoField label="Confianca" value={`${(detection.confidence * 100).toFixed(1)}%`} />
                  <InfoField label="Data/Hora" value={formatDate(detection.timestamp)} />
                  <InfoField label="Marca" value={detection.vehicle_brand} />
                  <InfoField label="Modelo" value={detection.vehicle_model} />
                  <InfoField label="Cor" value={detection.vehicle_color} />
                  <InfoField label="Tipo" value={detection.vehicle_type} />
                  <InfoField label="Ano" value={detection.vehicle_year?.toString()} />
                  <InfoField label="Cidade" value={detection.city} />
                  <InfoField label="Direcao" value={detection.direction} />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Fullscreen image viewer */}
      {imageExpanded && imageUrl && (
        <div
          className="fixed inset-0 z-[60] flex items-center justify-center bg-black/95 cursor-pointer"
          onClick={() => setImageExpanded(false)}
        >
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-4 right-4 text-white hover:bg-white/10"
            onClick={() => setImageExpanded(false)}
          >
            <X className="w-6 h-6" />
          </Button>
          <img src={imageUrl} alt="Frame expandido" className="max-w-[95vw] max-h-[95vh] object-contain" />
        </div>
      )}
    </>
  )
}

function InfoField({ label, value }: { label: string; value?: string | null }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-sm font-medium">{value || '-'}</p>
    </div>
  )
}
