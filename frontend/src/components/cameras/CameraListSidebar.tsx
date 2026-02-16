import { useState, useMemo } from 'react'
import { Camera } from '@/types'
import { useCameraStore } from '@/store/cameraStore'
import { StreamThumbnail } from './StreamThumbnail'
import { Search, Filter } from 'lucide-react'

interface CameraListSidebarProps {
  selectedCamera: Camera | null
  onCameraSelect: (camera: Camera) => void
  onCameraHover: (camera: Camera | null) => void
}

export function CameraListSidebar({ selectedCamera, onCameraSelect, onCameraHover }: CameraListSidebarProps) {
  const { cameras } = useCameraStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | 'online' | 'offline'>('all')

  const filteredCameras = useMemo(() => {
    return cameras.filter(camera => {
      const matchesSearch = camera.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           camera.location?.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesStatus = statusFilter === 'all' || camera.status === statusFilter
      return matchesSearch && matchesStatus
    })
  }, [cameras, searchTerm, statusFilter])

  return (
    <div className="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold mb-3">Câmeras</h2>
        
        {/* Search */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar câmera..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          />
        </div>

        {/* Filter */}
        <div className="flex gap-2">
          <button
            onClick={() => setStatusFilter('all')}
            className={`flex-1 px-3 py-1.5 text-xs rounded ${
              statusFilter === 'all' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            Todas ({cameras.length})
          </button>
          <button
            onClick={() => setStatusFilter('online')}
            className={`flex-1 px-3 py-1.5 text-xs rounded ${
              statusFilter === 'online' 
                ? 'bg-green-500 text-white' 
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            Online ({cameras.filter(c => c.status === 'online').length})
          </button>
          <button
            onClick={() => setStatusFilter('offline')}
            className={`flex-1 px-3 py-1.5 text-xs rounded ${
              statusFilter === 'offline' 
                ? 'bg-red-500 text-white' 
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            Offline ({cameras.filter(c => c.status === 'offline').length})
          </button>
        </div>
      </div>

      {/* Camera List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {filteredCameras.map(camera => (
          <div
            key={camera.id}
            onMouseEnter={() => onCameraHover(camera)}
            onMouseLeave={() => onCameraHover(null)}
            className={`border rounded-lg overflow-hidden transition-all ${
              selectedCamera?.id === camera.id
                ? 'border-blue-500 ring-2 ring-blue-500/20'
                : 'border-gray-200 dark:border-gray-700'
            }`}
          >
            <StreamThumbnail
              cameraId={camera.id}
              cameraName={camera.name}
              cameraStatus={camera.status}
              onClick={() => onCameraSelect(camera)}
            />
            {camera.location && (
              <div className="p-2 bg-gray-50 dark:bg-gray-900 text-xs text-gray-600 dark:text-gray-400">
                📍 {camera.location}
              </div>
            )}
          </div>
        ))}

        {filteredCameras.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            Nenhuma câmera encontrada
          </div>
        )}
      </div>
    </div>
  )
}
