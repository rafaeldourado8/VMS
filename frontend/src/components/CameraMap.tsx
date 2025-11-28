import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// --- Correção dos Ícones do Leaflet no Vite/React ---
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface Camera {
  id: number;
  name: string;
  location: string;
  latitude: number;
  longitude: number;
  status: string;
}

interface CameraMapProps {
  cameras: Camera[];
}

// Componente controlador interno para manipular o mapa
const MapController = ({ cameras }: CameraMapProps) => {
  const map = useMap();

  useEffect(() => {
    // 1. O "Pulo do Gato": Força o Leaflet a recalcular o tamanho do container
    // Isso corrige o bug onde o mapa não preenche o espaço ou vaza a tela
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 100);

    // 2. Ajusta o zoom para mostrar todos os marcadores (se houver)
    const validCameras = (Array.isArray(cameras) ? cameras : []).filter(c => c.latitude && c.longitude);
    if (validCameras.length > 0) {
      const bounds = L.latLngBounds(validCameras.map(c => [c.latitude, c.longitude]));
      map.fitBounds(bounds, { padding: [50, 50] });
    }

    return () => clearTimeout(timer);
  }, [cameras, map]);

  return null;
};

const CameraMap = ({ cameras }: CameraMapProps) => {
  const camerasWithCoords = cameras.filter(c => c.latitude && c.longitude);

  return (
    // 'w-full' garante que ocupa 100% da largura do pai
    // 'isolate z-0' garante que o mapa não fique por cima de menus/dropdowns
    <div className="h-[500px] w-full rounded-lg border border-border overflow-hidden relative z-0 isolate">
      <MapContainer 
        center={[-15.7801, -47.9292]} 
        zoom={4} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {camerasWithCoords.map((camera) => (
          <Marker key={camera.id} position={[camera.latitude, camera.longitude]}>
            <Popup>
              <div className="font-sans">
                <h3 className="font-bold text-base mb-2">{camera.name}</h3>
                <p className="m-0 text-sm">
                  <strong>Local:</strong> {camera.location}
                </p>
                <p className="m-0 text-sm">
                  <strong>Status:</strong> 
                  <span className={camera.status === 'online' ? 'text-green-600' : 'text-gray-500'}>
                    {camera.status === 'online' ? ' Online' : ' Offline'}
                  </span>
                </p>
              </div>
            </Popup>
          </Marker>
        ))}
        
        <MapController cameras={camerasWithCoords} />
      </MapContainer>
    </div>
  );
};

export default CameraMap;