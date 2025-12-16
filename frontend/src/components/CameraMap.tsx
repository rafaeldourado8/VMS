// Leaflet removido - usar MapViewer (Google Maps) em vez disso

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

const CameraMap = ({ cameras }: CameraMapProps) => {
  return (
    <div className="h-[500px] w-full rounded-lg border border-border overflow-hidden relative z-0">
      <div className="flex items-center justify-center h-full bg-muted">
        <p className="text-muted-foreground">Use MapViewer component instead (Google Maps)</p>
      </div>
    </div>
  );
};

export default CameraMap;