import { useEffect, useRef, useState } from 'react'
import { Camera } from '@/types'
import { useCameraStore } from '@/store/cameraStore'
import { Loader2 } from 'lucide-react'

interface CameraMapProps {
  selectedCamera: Camera | null
  hoveredCamera: Camera | null
  onCameraClick: (camera: Camera) => void
  onCameraHover: (camera: Camera | null) => void
}

export function CameraMap({ selectedCamera, hoveredCamera, onCameraClick, onCameraHover }: CameraMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const googleMapRef = useRef<any>(null)
  const markersRef = useRef<Map<number, any>>(new Map())
  const { cameras } = useCameraStore()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Inicializar Google Maps
  useEffect(() => {
    if (!mapRef.current) return

    const initMap = () => {
      try {
        if (!window.google?.maps?.Map) {
          setError('Google Maps não carregou corretamente')
          setIsLoading(false)
          return
        }

        const map = new window.google.maps.Map(mapRef.current!, {
          center: { lat: -23.5505, lng: -46.6333 },
          zoom: 12,
          mapTypeControl: true,
          streetViewControl: false,
          fullscreenControl: true,
        })

        googleMapRef.current = map
        setIsLoading(false)
      } catch (err) {
        console.error('Erro ao inicializar mapa:', err)
        setError('Erro ao carregar mapa')
        setIsLoading(false)
      }
    }

    // Carregar Google Maps API
    if (!window.google?.maps) {
      const existingScript = document.querySelector('script[src*="maps.googleapis.com"]')
      if (existingScript) {
        existingScript.addEventListener('load', initMap)
        return
      }

      const script = document.createElement('script')
      script.src = `https://maps.googleapis.com/maps/api/js?key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`
      script.async = true
      script.onload = initMap
      script.onerror = () => {
        setError('Falha ao carregar Google Maps')
        setIsLoading(false)
      }
      document.head.appendChild(script)
    } else {
      initMap()
    }
  }, [])

  // Atualizar marcadores quando câmeras mudarem
  useEffect(() => {
    if (!googleMapRef.current) return

    const map = googleMapRef.current
    const camerasWithLocation = cameras.filter(c => c.latitude && c.longitude)

    // Remover marcadores antigos
    markersRef.current.forEach(marker => marker.setMap(null))
    markersRef.current.clear()

    // Se não há câmeras com localização, não criar marcadores
    if (camerasWithLocation.length === 0) return

    // Criar novos marcadores
    camerasWithLocation.forEach(camera => {
      const marker = new google.maps.Marker({
        position: { lat: camera.latitude!, lng: camera.longitude! },
        map,
        title: camera.name,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 10,
          fillColor: camera.status === 'online' ? '#10b981' : '#ef4444',
          fillOpacity: 1,
          strokeColor: '#ffffff',
          strokeWeight: 2,
        },
      })

      marker.addListener('click', () => onCameraClick(camera))
      marker.addListener('mouseover', () => onCameraHover(camera))
      marker.addListener('mouseout', () => onCameraHover(null))

      markersRef.current.set(camera.id, marker)
    })

    // Ajustar bounds para mostrar todas as câmeras
    const bounds = new google.maps.LatLngBounds()
    camerasWithLocation.forEach(camera => {
      bounds.extend({ lat: camera.latitude!, lng: camera.longitude! })
    })
    map.fitBounds(bounds)
  }, [cameras, onCameraClick, onCameraHover])

  // Destacar câmera selecionada ou hover
  useEffect(() => {
    const highlightedCamera = selectedCamera || hoveredCamera
    
    markersRef.current.forEach((marker, cameraId) => {
      const camera = cameras.find(c => c.id === cameraId)
      if (!camera) return

      const isHighlighted = highlightedCamera?.id === cameraId
      const baseColor = camera.status === 'online' ? '#10b981' : '#ef4444'

      marker.setIcon({
        path: google.maps.SymbolPath.CIRCLE,
        scale: isHighlighted ? 14 : 10,
        fillColor: baseColor,
        fillOpacity: 1,
        strokeColor: isHighlighted ? '#fbbf24' : '#ffffff',
        strokeWeight: isHighlighted ? 3 : 2,
      })
    })
  }, [selectedCamera, hoveredCamera, cameras])

  return (
    <div className="relative w-full h-full bg-gray-100 dark:bg-gray-900">
      <div ref={mapRef} className="w-full h-full" />
      
      {isLoading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-blue-500">
          <Loader2 className="w-12 h-12 animate-spin text-white mb-4" />
          <p className="text-white text-lg">Carregando Google Maps...</p>
        </div>
      )}

      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-red-500">
          <p className="text-white text-lg mb-2">{error}</p>
          <p className="text-white text-sm">Verifique a API Key do Google Maps</p>
        </div>
      )}

      {!isLoading && !error && cameras.filter(c => c.latitude && c.longitude).length === 0 && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
          <div className="text-center p-8">
            <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center">
              <svg className="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-2">Nenhuma câmera no mapa</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">Adicione coordenadas GPS às suas câmeras para visualizá-las aqui</p>
            <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
              Adicionar Câmera
            </button>
          </div>
        </div>
      )}

      {/* Stats overlay */}
      {!isLoading && !error && cameras.filter(c => c.latitude && c.longitude).length > 0 && (
        <div className="absolute top-4 right-4 flex gap-2">
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur rounded-lg shadow-lg px-4 py-2">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-sm font-medium">{cameras.filter(c => c.status === 'online').length} Online</span>
            </div>
          </div>
          <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur rounded-lg shadow-lg px-4 py-2">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-red-500" />
              <span className="text-sm font-medium">{cameras.filter(c => c.status === 'offline').length} Offline</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
