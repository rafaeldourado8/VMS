import { useState, useCallback, useEffect, useRef } from "react";
import { GoogleMap, useJsApiLoader, MarkerF, InfoWindowF } from "@react-google-maps/api";
import { Camera as CameraIcon, Maximize2, MapPin } from "lucide-react";
import { CameraStatusBadge } from "./CameraStatusBadge"; // Importando o componente isolado

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "";

// Interfaces
export interface Camera {
  id: number;
  name: string;
  location: string;
  latitude?: number;
  longitude?: number;
  status: "online" | "offline" | "lpr";
  thumbnail_url?: string | null;
  stream_url?: string;
}

interface MapViewerProps {
  cameras?: Camera[];
  height?: string;
  zoom?: number;
  onCameraDoubleClick?: (camera: Camera) => void;
}

// Estilos e Configurações do Mapa
const mapContainerStyle = {
  width: "100%",
  height: "100%",
};

const defaultCenter = { lat: -15.7801, lng: -47.9292 };

// SVG do Pino Customizado (Estilo Gota Moderna)
const PIN_SVG_PATH = "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z";

export default function MapViewer({
  cameras = [],
  height = "500px",
  zoom = 13,
  onCameraDoubleClick,
}: MapViewerProps) {
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);
  const [map, setMap] = useState<google.maps.Map | null>(null);
  
  // Controle de clique duplo vs clique simples
  const clickTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: API_KEY,
  });

  // Filtra apenas câmeras com coordenadas válidas
  const validCameras = cameras.filter(
    (c) => c.latitude !== undefined && c.latitude !== null && c.longitude !== undefined && c.longitude !== null
  );

  const onLoad = useCallback((mapInstance: google.maps.Map) => {
    setMap(mapInstance);
  }, []);

  // Monitorar Zoom para fechar popup se ficar muito longe (limpeza visual)
  const handleZoomChanged = () => {
    if (map) {
      const currentZoom = map.getZoom();
      if (currentZoom && currentZoom < 10 && selectedCamera) {
        setSelectedCamera(null);
      }
    }
  };

  // Ajuste inicial de limites do mapa (Fit Bounds)
  useEffect(() => {
    if (map && validCameras.length > 0 && !selectedCamera) {
      const bounds = new google.maps.LatLngBounds();
      let hasValidBounds = false;

      validCameras.forEach((c) => {
        const lat = Number(c.latitude);
        const lng = Number(c.longitude);
        // Proteção extra contra coordenadas inválidas (0,0 ou NaN)
        if (!isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0) {
            bounds.extend({ lat, lng });
            hasValidBounds = true;
        }
      });

      if (hasValidBounds) {
          map.fitBounds(bounds);
      }
    }
  }, [map, validCameras.length]); // Removido selectedCamera das deps para não resetar zoom ao clicar

  const handleMarkerClick = (camera: Camera) => {
    setSelectedCamera(camera);
    
    // UX: Centraliza suavemente e aproxima ao clicar no pino
    if (map) {
        const lat = Number(camera.latitude);
        const lng = Number(camera.longitude);
        
        map.panTo({ lat, lng });
        
        const currentZoom = map.getZoom();
        // Se estiver muito longe, aproxima para nível de rua
        if (currentZoom && currentZoom < 16) {
            setTimeout(() => map.setZoom(16), 300); // Pequeno delay para a animação do Pan terminar
        }
    }
  };

  const handleInfoWindowClick = (e: React.MouseEvent, camera: Camera) => {
    // Evita propagação se clicar em botões internos
    if ((e.target as HTMLElement).closest('button')) return;

    if (clickTimeoutRef.current) {
        // Double Click Detectado
        clearTimeout(clickTimeoutRef.current);
        clickTimeoutRef.current = null;
        if (onCameraDoubleClick) onCameraDoubleClick(camera);
    } else {
        // Single Click - Aguarda um pouco para ver se vira double click
        clickTimeoutRef.current = setTimeout(() => {
            clickTimeoutRef.current = null;
        }, 250); 
    }
  };

  if (!isLoaded) return <div style={{ height }} className="w-full h-full bg-muted animate-pulse rounded-lg flex items-center justify-center text-muted-foreground">Carregando Mapa...</div>;
  if (loadError) return <div className="flex items-center justify-center h-full text-red-500 bg-red-50 rounded-lg border border-red-200">Erro ao carregar Google Maps API</div>;

  return (
    <div style={{ height }} className="w-full h-full relative z-0">
      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        center={defaultCenter}
        zoom={zoom}
        onLoad={onLoad}
        onZoomChanged={handleZoomChanged}
        options={{
          mapTypeControl: false,
          fullscreenControl: false,
          streetViewControl: false,
          zoomControl: true,
          zoomControlOptions: { position: 9 }, // Bottom Right
          gestureHandling: "cooperative", // Melhora scroll na página
          styles: [
            // Estilo Clean/Dark simplificado para destacar os pinos
            { featureType: "poi", elementType: "labels", stylers: [{ visibility: "off" }] },
            { featureType: "transit", elementType: "labels", stylers: [{ visibility: "off" }] }
          ],
        }}
      >
        {validCameras.map((camera) => (
          <MarkerF
            key={camera.id}
            position={{ lat: Number(camera.latitude), lng: Number(camera.longitude) }}
            onClick={() => handleMarkerClick(camera)}
            icon={{
              path: PIN_SVG_PATH,
              fillColor: camera.status === 'online' ? "#10b981" : "#ef4444", // Verde ou Vermelho no pino
              fillOpacity: 1,
              strokeColor: "#FFFFFF",
              strokeWeight: 2,
              scale: 2,
              anchor: new google.maps.Point(12, 22), 
              labelOrigin: new google.maps.Point(12, 9),
            }}
          >
            {selectedCamera?.id === camera.id && (
              <InfoWindowF
                onCloseClick={() => setSelectedCamera(null)}
                options={{ 
                    pixelOffset: new google.maps.Size(0, -30), 
                    disableAutoPan: false,
                    maxWidth: 320 
                }}
              >
                <div 
                    className="bg-white rounded-lg overflow-hidden flex flex-col font-sans shadow-sm cursor-pointer group w-[260px]"
                    onClick={(e) => handleInfoWindowClick(e as any, camera)}
                >
                  {/* Área da Imagem / Thumbnail */}
                  <div className="relative h-36 w-full bg-slate-100 flex items-center justify-center overflow-hidden">
                    {/* Fallback (Fundo) */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400 bg-slate-200 z-0">
                        <CameraIcon size={32} strokeWidth={1.5} />
                        <span className="text-[10px] font-medium mt-2 uppercase tracking-widest">Sem Sinal</span>
                    </div>

                    {/* Imagem Real (Se existir e carregar) */}
                    {camera.thumbnail_url && (
                        <img 
                            src={camera.thumbnail_url} 
                            alt={camera.name} 
                            className="w-full h-full object-cover z-10 transition-transform duration-700 group-hover:scale-105"
                            onError={(e) => {
                                // Esconde a imagem quebrada para revelar o fallback atrás
                                e.currentTarget.style.display = 'none';
                            }}
                        />
                    )}

                    {/* Overlay de Ação no Hover */}
                    <div className="absolute inset-0 bg-black/40 z-20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center backdrop-blur-[2px]">
                        <span className="bg-white text-black text-xs font-bold px-3 py-1.5 rounded-full flex items-center gap-1.5 shadow-lg transform translate-y-2 group-hover:translate-y-0 transition-transform">
                            <Maximize2 className="w-3.5 h-3.5"/> Abrir Player
                        </span>
                    </div>

                    {/* Tag "Ao Vivo" (Apenas visual) */}
                    {camera.status === 'online' && (
                        <div className="absolute top-2 left-2 z-20 bg-red-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded shadow-sm flex items-center gap-1 animate-pulse">
                            <span className="w-1.5 h-1.5 bg-white rounded-full"/> LIVE
                        </div>
                    )}
                  </div>
                  
                  {/* Informações da Câmera */}
                  <div className="p-3 border-t border-slate-100">
                    <div className="flex justify-between items-start mb-1">
                        <h3 className="font-bold text-slate-800 text-sm leading-tight truncate pr-2 flex-1">
                            {camera.name}
                        </h3>
                        <CameraStatusBadge status={camera.status} />
                    </div>
                    
                    <div className="flex items-center gap-1.5 text-slate-500 mt-1">
                        <MapPin className="w-3 h-3 shrink-0" />
                        <p className="text-xs font-medium uppercase tracking-wide truncate">
                            {camera.location || "Localização não definida"}
                        </p>
                    </div>
                  </div>
                </div>
              </InfoWindowF>
            )}
          </MarkerF>
        ))}
      </GoogleMap>
    </div>
  );
}