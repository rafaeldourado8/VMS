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
      const isOnline = camera.status === 'online'
      
      // Ícone SVG customizado de câmera
      const cameraIcon = {
        url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
          <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="2"/>
                <feOffset dx="0" dy="2" result="offsetblur"/>
                <feComponentTransfer>
                  <feFuncA type="linear" slope="0.3"/>
                </feComponentTransfer>
                <feMerge>
                  <feMergeNode/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            <circle cx="20" cy="20" r="16" fill="${isOnline ? '#10b981' : '#ef4444'}" filter="url(#shadow)"/>
            <circle cx="20" cy="20" r="16" fill="none" stroke="white" stroke-width="2"/>
            <path d="M14 16 L14 24 L22 20 Z" fill="white"/>
            <circle cx="26" cy="14" r="3" fill="${isOnline ? '#34d399' : '#f87171'}" stroke="white" stroke-width="1"/>
          </svg>
        `)}`,
        scaledSize: new google.maps.Size(40, 40),
        anchor: new google.maps.Point(20, 20)
      }

      const marker = new google.maps.Marker({
        position: { lat: camera.latitude!, lng: camera.longitude! },
        map,
        title: camera.name,
        icon: cameraIcon,
        animation: isOnline ? google.maps.Animation.DROP : undefined
      })

      // InfoWindow com preview e snapshot
      const snapshotUrl = `/streaming/cameras/${camera.id}/snapshot`
      const locationText = camera.location ? camera.location.substring(0, 50) + (camera.location.length > 50 ? '...' : '') : ''
      const infoWindow = new google.maps.InfoWindow({
        content: `
          <div style="padding: 0; min-width: 250px; max-width: 300px;">
            <img src="${snapshotUrl}" 
                 style="width: 100%; height: 150px; object-fit: cover; border-radius: 8px 8px 0 0; background: #1f2937; display: block;"
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='flex'"
                 alt="${camera.name}" 
                 crossorigin="anonymous" />
            <div style="display: none; width: 100%; height: 150px; background: #1f2937; border-radius: 8px 8px 0 0; align-items: center; justify-content: center; flex-direction: column; gap: 8px;">
              <svg width="32" height="32" fill="#9ca3af" viewBox="0 0 20 20">
                <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z"/>
              </svg>
              <span style="color: #9ca3af; font-size: 12px;">Sem snapshot</span>
            </div>
            <div style="padding: 12px;">
              <h3 style="margin: 0 0 8px 0; font-weight: 600; color: #1f2937; font-size: 16px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${camera.name}</h3>
              <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 6px;">
                <div style="width: 8px; height: 8px; border-radius: 50%; background: ${isOnline ? '#10b981' : '#ef4444'}; ${isOnline ? 'animation: pulse 2s infinite;' : ''}"></div>
                <span style="font-size: 14px; color: #6b7280; font-weight: 500;">${isOnline ? 'Online' : 'Offline'}</span>
              </div>
              ${locationText ? `<p style="margin: 4px 0 0 0; font-size: 12px; color: #9ca3af; display: flex; align-items: flex-start; gap: 4px; line-height: 1.4;">
                <svg width="12" height="12" fill="currentColor" viewBox="0 0 20 20" style="flex-shrink: 0; margin-top: 2px;">
                  <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"/>
                </svg>
                <span style="word-break: break-word;">${locationText}</span>
              </p>` : ''}
            </div>
          </div>
          <style>
            @keyframes pulse {
              0%, 100% { opacity: 1; }
              50% { opacity: 0.5; }
            }
          </style>
        `
      })

      marker.addListener('click', () => {
        infoWindow.open(map, marker)
        onCameraClick(camera)
      })
      
      marker.addListener('mouseover', () => {
        infoWindow.open(map, marker)
        onCameraHover(camera)
      })
      
      marker.addListener('mouseout', () => {
        setTimeout(() => {
          if (!selectedCamera || selectedCamera.id !== camera.id) {
            infoWindow.close()
          }
        }, 200)
        onCameraHover(null)
      })

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
      const isOnline = camera.status === 'online'
      const scale = isHighlighted ? 1.3 : 1
      
      const cameraIcon = {
        url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(`
          <svg width="${40 * scale}" height="${40 * scale}" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur in="SourceAlpha" stdDeviation="${isHighlighted ? 3 : 2}"/>
                <feOffset dx="0" dy="2" result="offsetblur"/>
                <feComponentTransfer>
                  <feFuncA type="linear" slope="${isHighlighted ? 0.5 : 0.3}"/>
                </feComponentTransfer>
                <feMerge>
                  <feMergeNode/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            ${isHighlighted ? '<circle cx="20" cy="20" r="18" fill="none" stroke="#fbbf24" stroke-width="2" opacity="0.6"/>' : ''}
            <circle cx="20" cy="20" r="16" fill="${isOnline ? '#10b981' : '#ef4444'}" filter="url(#shadow)"/>
            <circle cx="20" cy="20" r="16" fill="none" stroke="${isHighlighted ? '#fbbf24' : 'white'}" stroke-width="${isHighlighted ? 3 : 2}"/>
            <path d="M14 16 L14 24 L22 20 Z" fill="white"/>
            <circle cx="26" cy="14" r="3" fill="${isOnline ? '#34d399' : '#f87171'}" stroke="white" stroke-width="1"/>
          </svg>
        `)}`,
        scaledSize: new google.maps.Size(40 * scale, 40 * scale),
        anchor: new google.maps.Point(20 * scale, 20 * scale)
      }
      
      marker.setIcon(cameraIcon)
      if (isHighlighted) {
        marker.setZIndex(1000)
      } else {
        marker.setZIndex(undefined)
      }
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
