import { useState, useCallback, useEffect, useRef } from "react";
import { GoogleMap, useJsApiLoader, MarkerF, InfoWindowF } from "@react-google-maps/api";
import { Camera as CameraIcon, Maximize2 } from "lucide-react";

const API_KEY = import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "";

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

const mapContainerStyle = {
  width: "100%",
  height: "100%",
};

const defaultCenter = { lat: -15.7801, lng: -47.9292 };
// SVG do Pino (Gota)
const PIN_SVG_PATH = "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z";

export default function MapViewer({
  cameras = [],
  height = "500px",
  zoom = 13,
  onCameraDoubleClick,
}: MapViewerProps) {
  const [selectedCamera, setSelectedCamera] = useState<Camera | null>(null);
  const [map, setMap] = useState<google.maps.Map | null>(null);
  
  // Controle de clique duplo
  const clickTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: API_KEY,
  });

  const validCameras = cameras.filter(
    (c) => c.latitude !== undefined && c.latitude !== null && c.longitude !== undefined && c.longitude !== null
  );

  const onLoad = useCallback((mapInstance: google.maps.Map) => {
    setMap(mapInstance);
  }, []);

  // Monitorar Zoom para fechar popup se ficar muito longe
  const handleZoomChanged = () => {
    if (map) {
      const currentZoom = map.getZoom();
      // Se o usuário tirar muito o zoom (ficar < 10), fecha o popup para não poluir
      if (currentZoom && currentZoom < 10 && selectedCamera) {
        setSelectedCamera(null);
      }
    }
  };

  // Ajuste inicial de limites do mapa
  useEffect(() => {
    if (map && validCameras.length > 0 && !selectedCamera) {
      const bounds = new google.maps.LatLngBounds();
      validCameras.forEach((c) => bounds.extend({ lat: Number(c.latitude), lng: Number(c.longitude) }));
      map.fitBounds(bounds);
    }
  }, [map, validCameras, selectedCamera]);

  const handleMarkerClick = (camera: Camera) => {
    setSelectedCamera(camera);
    
    // MELHORIA DE UX: Centraliza e aproxima ao clicar no pino
    if (map) {
        map.panTo({ lat: Number(camera.latitude), lng: Number(camera.longitude) });
        const currentZoom = map.getZoom();
        // Se estiver muito longe, aproxima para nível de rua
        if (currentZoom && currentZoom < 15) {
            map.setZoom(15);
        }
    }
  };

  const handleInfoWindowClick = (e: React.MouseEvent, camera: Camera) => {
    // Evita propagação se clicar em botões internos
    if ((e.target as HTMLElement).closest('button')) return;

    if (clickTimeoutRef.current) {
        clearTimeout(clickTimeoutRef.current);
        clickTimeoutRef.current = null;
        if (onCameraDoubleClick) onCameraDoubleClick(camera);
    } else {
        clickTimeoutRef.current = setTimeout(() => {
            clickTimeoutRef.current = null;
        }, 250); 
    }
  };

  if (!isLoaded) return <div style={{ height }} className="w-full h-full bg-muted animate-pulse rounded-lg" />;
  if (loadError) return <div className="flex items-center justify-center h-full text-red-500">Erro ao carregar mapa</div>;

  return (
    <div style={{ height }} className="w-full h-full relative z-0">
      <GoogleMap
        mapContainerStyle={mapContainerStyle}
        center={defaultCenter}
        zoom={zoom}
        onLoad={onLoad}
        onZoomChanged={handleZoomChanged} // Listener de Zoom
        options={{
          mapTypeControl: false,
          fullscreenControl: false,
          streetViewControl: false,
          zoomControl: true,
          zoomControlOptions: { position: 9 }, // Bottom Right
          gestureHandling: "cooperative", // Melhora scroll na página
          styles: [{ featureType: "poi", elementType: "labels", stylers: [{ visibility: "off" }] }],
        }}
      >
        {validCameras.map((camera) => (
          <MarkerF
            key={camera.id}
            position={{ lat: Number(camera.latitude), lng: Number(camera.longitude) }}
            onClick={() => handleMarkerClick(camera)}
            icon={{
              path: PIN_SVG_PATH,
              fillColor: "#0088FF",
              fillOpacity: 1,
              strokeColor: "#FFFFFF",
              strokeWeight: 2,
              scale: 2,
              // Ajuste fino para a ponta do pino tocar o local exato
              anchor: new google.maps.Point(12, 22), 
              labelOrigin: new google.maps.Point(12, 9),
            }}
          >
            {selectedCamera?.id === camera.id && (
              <InfoWindowF
                onCloseClick={() => setSelectedCamera(null)}
                // PixelOffset ajustado para o popup não cobrir o pino
                options={{ pixelOffset: new google.maps.Size(0, -30), disableAutoPan: false }}
              >
                <div 
                    className="w-[85vw] max-w-[280px] bg-white rounded-lg overflow-hidden flex flex-col font-sans shadow-none cursor-pointer"
                    onClick={(e) => handleInfoWindowClick(e as any, camera)}
                >
                  <div className="relative h-32 sm:h-36 w-full bg-slate-100 group">
                    {camera.thumbnail_url ? (
                      <img src={camera.thumbnail_url} alt={camera.name} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-slate-200 text-slate-400">
                        <CameraIcon size={32} />
                      </div>
                    )}
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <span className="bg-black/60 text-white text-[10px] px-2 py-1 rounded-full flex items-center gap-1 backdrop-blur-sm">
                            <Maximize2 className="w-3 h-3"/> Abrir
                        </span>
                    </div>
                    <div className="absolute bottom-2 right-2 bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow-sm">
                      Ao Vivo
                    </div>
                  </div>
                  
                  <div className="p-3 sm:p-4 border-t border-slate-100">
                    <h3 className="font-bold text-slate-800 text-sm sm:text-base leading-tight mb-1 truncate">
                        {camera.name}
                    </h3>
                    <p className="text-[10px] sm:text-xs text-slate-500 font-medium uppercase tracking-wide mb-2 truncate">
                      {camera.location || "Localização desconhecida"}
                    </p>
                    <div className="flex items-center gap-1.5">
                      <span className={`flex h-2 w-2 rounded-full ${camera.status === 'online' ? 'bg-green-500' : 'bg-red-500'}`} />
                      <span className="text-[10px] sm:text-[11px] uppercase font-bold text-slate-400 tracking-wider">
                        {camera.status === 'online' ? 'ONLINE' : 'OFFLINE'}
                      </span>
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