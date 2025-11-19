import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface User {
  id: number;
  email: string;
  name: string;
  role: 'admin' | 'viewer';
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      
      logout: () => {
        // Remove os tokens da memória da sessão
        sessionStorage.removeItem('access_token');
        sessionStorage.removeItem('refresh_token');
        // Limpa o estado do Zustand
        set({ user: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage', // Nome único para guardar no storage
      // AQUI ESTÁ A CORREÇÃO: Usar sessionStorage em vez de localStorage
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);