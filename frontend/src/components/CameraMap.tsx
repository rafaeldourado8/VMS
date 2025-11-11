import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css'; // Importa o CSS do Leaflet
import L from 'leaflet';

// --- Início da Correção de Ícone ---
// Isto corrige um problema comum do Leaflet com o Vite/React
// onde os ícones dos marcadores não aparecem.
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
// --- Fim da Correção de Ícone ---

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

// Componente auxiliar para centrar o mapa automaticamente
const MapBounds = ({ cameras }: CameraMapProps) => {
  const map = useMap();
  useEffect(() => {
    const validCameras = cameras.filter(c => c.latitude && c.longitude);
    if (validCameras.length > 0) {
      // Cria um 'bound' (limite) que engloba todas as câmaras
      const bounds = L.latLngBounds(validCameras.map(c => [c.latitude, c.longitude]));
      // Ajusta o mapa a esses limites com um padding
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [cameras, map]);
  return null;
}

const CameraMap = ({ cameras }: CameraMapProps) => {
  // Filtra câmaras que têm coordenadas válidas
  const camerasWithCoords = cameras.filter(c => c.latitude && c.longitude);

  return (
    <div className="h-[500px] rounded-lg border border-border overflow-hidden">
      <MapContainer 
        center={[-15.7801, -47.9292]} // Centro padrão (Brasília) se não houver câmaras
        zoom={4} 
        style={{ height: '100%', width: '100%' }}
      >
        {/* Camada do mapa base (OpenStreetMap) */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* Mapeia as câmaras e cria um Marcador (Marker) para cada uma */}
        {camerasWithCoords.map((camera) => (
          <Marker key={camera.id} position={[camera.latitude, camera.longitude]}>
            <Popup>
              {/* Conteúdo do popup ao clicar */}
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
        
        {/* Componente que ajusta o zoom e o centro do mapa automaticamente */}
        <MapBounds cameras={camerasWithCoords} />
      </MapContainer>
    </div>
  );
};

export default CameraMap;