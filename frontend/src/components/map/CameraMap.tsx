import { APIProvider, Map, AdvancedMarker, InfoWindow } from '@vis.gl/react-google-maps'
import { useState } from 'react'
import { Camera as CameraType } from '@/domain/entities/Camera'
import { Camera, MapPin } from 'lucide-react'

interface CameraMapProps {
  cameras: CameraType[]
  apiKey: string
  center?: { lat: number; lng: number }
  zoom?: number
}

export function CameraMap({ cameras, apiKey, center, zoom = 12 }: CameraMapProps) {
  const [selectedCamera, setSelectedCamera] = useState<CameraType | null>(null)

  const defaultCenter = center || {
    lat: cameras[0]?.latitude || -15.7942,
    lng: cameras[0]?.longitude || -47.8822,
  }

  const camerasWithLocation = cameras.filter((cam) => cam.latitude && cam.longitude)

  return (
    <APIProvider apiKey={apiKey}>
      <div className="w-full h-full rounded-lg overflow-hidden">
        <Map
          defaultCenter={defaultCenter}
          defaultZoom={zoom}
          mapId="vms-camera-map"
          disableDefaultUI={false}
          gestureHandling="greedy"
        >
          {camerasWithLocation.map((camera) => (
            <AdvancedMarker
              key={camera.id}
              position={{ lat: camera.latitude!, lng: camera.longitude! }}
              onClick={() => setSelectedCamera(camera)}
            >
              <div
                className={`p-2 rounded-full shadow-lg ${
                  camera.status === 'online' ? 'bg-emerald-500' : 'bg-red-500'
                }`}
              >
                <Camera className="w-4 h-4 text-white" />
              </div>
            </AdvancedMarker>
          ))}

          {selectedCamera && (
            <InfoWindow
              position={{
                lat: selectedCamera.latitude!,
                lng: selectedCamera.longitude!,
              }}
              onCloseClick={() => setSelectedCamera(null)}
            >
              <div className="p-2 min-w-[200px]">
                <h3 className="font-semibold text-sm mb-1">{selectedCamera.name}</h3>
                {selectedCamera.location && (
                  <p className="text-xs text-gray-600 flex items-center gap-1 mb-2">
                    <MapPin className="w-3 h-3" />
                    {selectedCamera.location}
                  </p>
                )}
                <div className="flex items-center gap-2 text-xs">
                  <span
                    className={`px-2 py-0.5 rounded-full ${
                      selectedCamera.status === 'online'
                        ? 'bg-emerald-100 text-emerald-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {selectedCamera.status === 'online' ? 'Online' : 'Offline'}
                  </span>
                  {selectedCamera.aiEnabled && (
                    <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-700">
                      IA Ativa
                    </span>
                  )}
                </div>
              </div>
            </InfoWindow>
          )}
        </Map>
      </div>
    </APIProvider>
  )
}
