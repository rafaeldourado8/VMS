import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useEffect } from 'react';
import api from '@/lib/axios';

interface PrivateRouteProps {
  children: React.ReactNode;
}

const PrivateRoute = ({ children }: PrivateRouteProps) => {
  const { isAuthenticated, setUser } = useAuthStore();

  useEffect(() => {
    const checkAuth = async () => {
      // ALTERADO: Ler do sessionStorage
      const token = sessionStorage.getItem('access_token');
      if (token && !isAuthenticated) {
        try {
          const response = await api.get('/auth/me/');
          setUser(response.data);
        } catch (error) {
          // ALTERADO: Limpar do sessionStorage
          sessionStorage.removeItem('access_token');
          sessionStorage.removeItem('refresh_token');
        }
      }
    };

    checkAuth();
  }, [isAuthenticated, setUser]);

  // ALTERADO: Ler do sessionStorage
  const token = sessionStorage.getItem('access_token');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export default PrivateRoute;