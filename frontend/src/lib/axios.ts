// frontend/src/lib/axios.ts
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import { clearAuthTokens, getAccessToken, getRefreshToken, setAccessToken } from './utils';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

type PendingRequest = {
  resolve: (value?: any) => void;
  reject: (error?: any) => void;
  config: AxiosRequestConfig;
};

const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // se usar cookies / sesssion-based auth
});

/**
 * Request interceptor: adiciona Authorization header se houver token
 */
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) {
      config.headers = config.headers ?? {};
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

/**
 * Response interceptor com lógica de refresh token.
 * - Em 401 (Unauthorized) = tentamos refresh token (uma vez).
 * - Uso de fila para evitar múltiplos refresh simultâneos.
 */

let isRefreshing = false;
let failedQueue: PendingRequest[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((p) => {
    if (error) {
      p.reject(error);
    } else {
      if (token) {
        p.config.headers = p.config.headers ?? {};
        p.config.headers['Authorization'] = `Bearer ${token}`;
        p.resolve(api(p.config));
      } else {
        p.resolve(api(p.config));
      }
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError & { config?: AxiosRequestConfig }) => {
    const originalConfig = error?.config;

    // Se não existir config ou não for 401, repassa
    if (!originalConfig || error?.response?.status !== 401) {
      return Promise.reject(error);
    }

    // Marca para não entrar em loop de refresh (marcador _retry)
    if ((originalConfig as any)._retry) {
      // já tentou refresh e falhou
      return Promise.reject(error);
    }

    // Evita provocar interceptor para a chamada de refresh
    (originalConfig as any)._retry = true;

    try {
      if (isRefreshing) {
        // adiciona à fila e aguarda
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject, config: originalConfig });
        });
      }

      isRefreshing = true;

      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        // nada a fazer - limpa e redireciona
        clearAuthTokens();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      // Use axios sem interceptor para evitar loop
      const plain = axios.create({
        baseURL: API_BASE,
        withCredentials: true,
        headers: { 'Content-Type': 'application/json' },
      });

      // Ajuste o path caso seu endpoint seja diferente
      const resp = await plain.post('/auth/refresh/', { refresh: refreshToken });

      const newAccess = (resp.data && (resp.data.access || resp.data.token || resp.data.access_token)) ?? null;
      if (!newAccess) {
        throw new Error('Refresh tentou mas não retornou access token');
      }

      // Armazena novo token
      setAccessToken(newAccess);

      // Processa fila com token novo
      processQueue(null, newAccess);

      // Re-executa a requisição original com novo token
      originalConfig.headers = originalConfig.headers ?? {};
      originalConfig.headers['Authorization'] = `Bearer ${newAccess}`;

      return api(originalConfig);
    } catch (refreshError) {
      processQueue(refreshError, null);
      clearAuthTokens();
      // redireciona para login
      window.location.href = '/login';
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);

export default api;