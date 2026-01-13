import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, Download, Calendar } from 'lucide-react'
import {
  Button,
  Input,
  Card,
  CardContent,
  Skeleton,
} from '@/components/ui'

interface Detection {
  id: number
  plate: string
  camera_name: string
  detected_at: string
  confidence: number
  vehicle_brand?: string
  vehicle_model?: string
  vehicle_color?: string
  vehicle_type?: string
  vehicle_year?: number
  city?: string
  plate_image: string
}

export function DetectionsPage() {
  const [filters, setFilters] = useState({
    camera: '',
    plate: '',
    dateFrom: '',
    dateTo: '',
    brand: '',
    color: '',
    blacklist: false,
    autoOCR: false,
  })

  // Mock data - substituir por API real
  const { data: detections, isLoading } = useQuery({
    queryKey: ['detections', filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters.camera) params.append('camera_id', filters.camera)
      if (filters.plate) params.append('plate', filters.plate)
      
      const response = await fetch(`http://localhost:8000/api/deteccoes/?${params}`)
      if (!response.ok) throw new Error('Failed to fetch detections')
      return response.json()
    },
  })

  const stats = {
    total: detections?.length || 0,
    high: detections?.filter(d => d.confidence >= 90).length || 0,
    medium: detections?.filter(d => d.confidence >= 75 && d.confidence < 90).length || 0,
    low: detections?.filter(d => d.confidence < 75).length || 0,
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Leitura de placa</h1>
          <p className="text-muted-foreground">Detecções de placas veiculares</p>
        </div>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Câmeras */}
            <div>
              <label className="text-sm font-medium mb-2 block text-gray-700">Câmeras</label>
              <select
                className="w-full px-3 py-2 border rounded-md bg-white text-gray-900"
                value={filters.camera}
                onChange={(e) => setFilters({ ...filters, camera: e.target.value })}
              >
                <option value="">Select</option>
                <option value="1">Câmera 1</option>
                <option value="2">Câmera 2</option>
              </select>
            </div>

            {/* Placa */}
            <div>
              <label className="text-sm font-medium mb-2 block text-gray-700">Placa</label>
              <Input
                placeholder="ABC1234"
                value={filters.plate}
                onChange={(e) => setFilters({ ...filters, plate: e.target.value })}
                className="bg-white text-gray-900"
              />
            </div>

            {/* Marca/Modelo */}
            <div>
              <label className="text-sm font-medium mb-2 block text-gray-700">Marca/Modelo</label>
              <Input
                placeholder="Toyota Hilux"
                value={filters.brand}
                onChange={(e) => setFilters({ ...filters, brand: e.target.value })}
                className="bg-white text-gray-900"
              />
            </div>

            {/* Cor */}
            <div>
              <label className="text-sm font-medium mb-2 block text-gray-700">Cor</label>
              <select
                className="w-full px-3 py-2 border rounded-md bg-white text-gray-900"
                value={filters.color}
                onChange={(e) => setFilters({ ...filters, color: e.target.value })}
              >
                <option value="">Todas</option>
                <option value="prata">Prata</option>
                <option value="branca">Branca</option>
                <option value="preta">Preta</option>
                <option value="vermelha">Vermelha</option>
              </select>
            </div>

            {/* Data Inicial */}
            <div>
              <label className="text-sm font-medium mb-2 block text-gray-700">Data inicial</label>
              <Input
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value })}
                className="bg-white text-gray-900"
              />
            </div>

            {/* Data Final */}
            <div>
              <label className="text-sm font-medium mb-2 block text-gray-700">Data final</label>
              <Input
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters({ ...filters, dateTo: e.target.value })}
                className="bg-white text-gray-900"
              />
            </div>

            {/* Checkboxes */}
            <div className="flex items-end gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={filters.blacklist}
                  onChange={(e) => setFilters({ ...filters, blacklist: e.target.checked })}
                />
                <span className="text-sm">Blacklist</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={filters.autoOCR}
                  onChange={(e) => setFilters({ ...filters, autoOCR: e.target.checked })}
                />
                <span className="text-sm">Auto OCR</span>
              </label>
            </div>

            {/* Botões */}
            <div className="flex items-end gap-2">
              <Button className="flex-1">
                <Search className="w-4 h-4 mr-2" />
                Buscar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gray-50 dark:bg-gray-800">
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900 dark:text-gray-100">{stats.total.toLocaleString()}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Registros</div>
              <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">Mostrar todos</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 dark:bg-purple-900/20">
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-700 dark:text-purple-400">{stats.high.toLocaleString()}</div>
              <div className="text-sm text-purple-700 dark:text-purple-400">Acima de 90%</div>
              <div className="text-xs text-purple-600 dark:text-purple-500 mt-1">7.9% do total</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-50 dark:bg-gray-800">
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900 dark:text-gray-100">{stats.medium.toLocaleString()}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Entre 75% e 90%</div>
              <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">37.6% do total</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gray-50 dark:bg-gray-800">
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-900 dark:text-gray-100">{stats.low.toLocaleString()}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Abaixo de 75%</div>
              <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">54.4% do total</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Ações */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {detections?.length || 0} detecções
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Relatório em EXCEL
          </Button>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Relatório em CSV
          </Button>
        </div>
      </div>

      {/* Tabela */}
      <Card>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-medium">Placa</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Nome da câmera</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Data</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Confiança</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Marca</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Modelo</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Cor</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Tipo</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Ano do modelo</th>
                  <th className="px-4 py-3 text-left text-sm font-medium">Cidade</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  Array.from({ length: 10 }).map((_, i) => (
                    <tr key={i} className="border-b">
                      <td className="px-4 py-3" colSpan={10}>
                        <Skeleton className="h-12 w-full" />
                      </td>
                    </tr>
                  ))
                ) : detections?.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="px-4 py-12 text-center text-muted-foreground">
                      Nenhuma detecção encontrada
                    </td>
                  </tr>
                ) : (
                  detections?.map((detection) => (
                    <tr key={detection.id} className="border-b hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <img
                            src={detection.plate_image}
                            alt={detection.plate}
                            className="w-16 h-10 object-cover rounded border"
                          />
                          <span className="font-mono font-semibold">{detection.plate}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm">{detection.camera_name}</td>
                      <td className="px-4 py-3 text-sm">
                        {new Date(detection.detected_at).toLocaleString('pt-BR')}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div
                            className={`w-2 h-2 rounded-full ${
                              detection.confidence >= 90
                                ? 'bg-green-500'
                                : detection.confidence >= 75
                                ? 'bg-yellow-500'
                                : 'bg-red-500'
                            }`}
                          />
                          <span className="text-sm">{detection.confidence.toFixed(2)}%</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-sm">{detection.vehicle_brand || '-'}</td>
                      <td className="px-4 py-3 text-sm">{detection.vehicle_model || '-'}</td>
                      <td className="px-4 py-3 text-sm">{detection.vehicle_color || '-'}</td>
                      <td className="px-4 py-3 text-sm">{detection.vehicle_type || '-'}</td>
                      <td className="px-4 py-3 text-sm">{detection.vehicle_year || '-'}</td>
                      <td className="px-4 py-3 text-sm">{detection.city || '-'}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
