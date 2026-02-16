import { useState, useEffect } from 'react'
import { Camera } from '@/types'
import { CameraMap } from '@/components/cameras/CameraMap'
import { CameraListSidebar } from '@/components/cameras/CameraListSidebar'
import { TimelinePlayerModal } from '@/components/cameras/TimelinePlayerModal'
import { useCameraStore } from '@/store/cameraStore'
import { cameraService } from '@/services/api'

export default function TacticalViewPage() {
  const { setCameras } = useCameraStore()
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null)
  const [hoveredCamera, setHoveredCamera] = useState<Camera | null>(null)

  useEffect(() => {
    const loadCameras = async () => {
      try {
        const data = await cameraService.list()
        setCameras(data)
      } catch (err) {
        console.error('Erro carregando câmeras:', err)
      }
    }
    loadCameras()
  }, [setCameras])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Visualização Tática</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Mapa com localização das câmeras e timeline de gravações
          </p>
        </div>
      </div>

      <div className="flex h-[calc(100vh-12rem)] bg-gray-50 dark:bg-gray-900 rounded-lg overflow-hidden border">
        {/* Mapa Principal */}
        <div className="flex-1 relative">
          <CameraMap
            selectedCamera={selectedCamera}
            hoveredCamera={hoveredCamera}
            onCameraClick={setSelectedCamera}
            onCameraHover={setHoveredCamera}
          />
        </div>

        {/* Sidebar com Lista de Câmeras */}
        <CameraListSidebar
          selectedCamera={selectedCamera}
          onCameraSelect={setSelectedCamera}
          onCameraHover={setHoveredCamera}
        />
      </div>

      {/* Modal do Player com Timeline */}
      {selectedCamera && (
        <TimelinePlayerModal
          camera={selectedCamera}
          onClose={() => setSelectedCamera(null)}
        />
      )}
    </div>
  )
}
