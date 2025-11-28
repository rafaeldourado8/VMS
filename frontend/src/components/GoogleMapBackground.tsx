import React, { useEffect, useRef, useState } from 'react';
import { Loader } from '@googlemaps/js-api-loader';
import api from '@/lib/axios';

interface Camera {
  id: number;
  name: string;
  latitude: number | string;
  longitude: number | string;
  status: string;
}

// React.memo previne re-renderizações se as props não mudarem (performance UI)
const GoogleMapBackground = React.memo(() => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const googleMapRef = useRef<google.maps.Map | null>(null);
  const markersRef = useRef<google.maps.Marker[]>([]);
  const [cameras, setCameras] = useState<Camera[]>([]);

  // 1. Buscar dados
  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const response = await api.get('/cameras/');
        const raw = response.data;
        const list = Array.isArray(raw) ? raw : (Array.isArray(raw?.results) ? raw.results : []);
        const validCameras = list.filter((c: any) => c.latitude && c.longitude);
        setCameras(validCameras);
      } catch (error) {
        console.error("Erro ao carregar câmeras no mapa de fundo", error);
      }
    };
    fetchCameras();
  }, []);

  // 2. Inicializar Mapa
  useEffect(() => {
    const initMap = async () => {
      const loader = new Loader({
        apiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "", 
        version: "weekly",
        libraries: ["places"]
      });

      try {
        const { Map } = await loader.importLibrary("maps") as google.maps.MapsLibrary;

        if (mapContainerRef.current && !googleMapRef.current) {
          googleMapRef.current = new Map(mapContainerRef.current, {
            center: { lat: -15.7942, lng: -47.8822 },
            zoom: 13,
            mapId: "DEMO_MAP_ID",
            disableDefaultUI: true,
            zoomControl: false,
            mapTypeControl: false,
            streetViewControl: false,
            fullscreenControl: false,
            gestureHandling: 'cooperative', 
            // Otimização: Rendering simplificado para fundo
            clickableIcons: false,
            styles: [ 
              { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
              { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
              { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
              { featureType: "administrative.locality", elementType: "labels.text.fill", stylers: [{ color: "#d59563" }] },
              { featureType: "road", elementType: "geometry", stylers: [{ color: "#38414e" }] },
              { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#212a37" }] },
              { featureType: "water", elementType: "geometry", stylers: [{ color: "#17263c" }] },
            ]
          });
        }
      } catch (error) {
        console.error("Erro ao inicializar Google Maps:", error);
      }
    };

    initMap();
  }, []);

  // 3. Gerenciar Marcadores
  useEffect(() => {
    if (!googleMapRef.current || cameras.length === 0) return;

    // Limpeza eficiente de marcadores
    markersRef.current.forEach((m) => m.setMap(null));
    markersRef.current = [];

    const bounds = new google.maps.LatLngBounds();

    cameras.forEach((camera) => {
      const lat = Number(camera.latitude);
      const lng = Number(camera.longitude);
      if (isNaN(lat) || isNaN(lng)) return;

      const position = { lat, lng };
      
      // Otimização: Marcador simples sem listeners complexos se for apenas fundo
      const marker = new google.maps.Marker({
        position,
        map: googleMapRef.current,
        title: camera.name,
        optimized: true, // Garante uso de canvas/WebGL
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 8,
          fillColor: camera.status === 'online' ? '#10b981' : '#ef4444',
          fillOpacity: 1,
          strokeColor: '#ffffff',
          strokeWeight: 2,
        },
      });

      markersRef.current.push(marker);
      bounds.extend(position);
    });

    if (!bounds.isEmpty()) {
      googleMapRef.current.fitBounds(bounds);
    }
  }, [cameras]);

  return (
    <div 
      ref={mapContainerRef} 
      className="absolute inset-0 w-full h-full z-0"
      // pointerEvents: none para garantir que o mapa de fundo não roube cliques
      style={{ pointerEvents: 'none' }} 
    />
  );
});

export default GoogleMapBackground;