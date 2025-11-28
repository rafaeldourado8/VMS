import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import GoogleMapBackground from './GoogleMapBackground';
import { cn } from '@/lib/utils';

const Layout = () => {
  const location = useLocation();
  
  // Adicionado '/live' e '/' para evitar duplicidade de mapas WebGL
  const hiddenMapRoutes = [
    '/', 
    '/live', 
    '/detections',
    '/admin',
    '/support',
    '/admin/users',
    '/admin/cameras'
  ];

  const isMapHidden = hiddenMapRoutes.some(route => 
    route === '/' ? location.pathname === '/' : location.pathname.startsWith(route)
  );

  const isFullWidthPage = location.pathname === '/' || location.pathname === '/live';

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      <Sidebar />
      
      <main className="flex-1 h-full relative overflow-hidden flex flex-col">
        
        {/* MELHORIA DE PERFORMANCE: 
            Renderização Condicional (!isMapHidden &&). 
            Isso DESMONTA o componente do DOM, liberando WebGL/GPU.
        */}
        {!isMapHidden && (
          <div className="absolute inset-0 z-0 transition-opacity duration-500 opacity-100">
             <GoogleMapBackground />
          </div>
        )}

        <div className={cn(
          "relative z-10 flex-1 overflow-y-auto scrollbar-thin",
          isFullWidthPage ? "p-0" : "p-6", 
          // Removemos a lógica de bg-color complexa pois agora o mapa é desmontado
          isMapHidden ? "bg-background" : "bg-black/40 backdrop-blur-sm"
        )}>
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;