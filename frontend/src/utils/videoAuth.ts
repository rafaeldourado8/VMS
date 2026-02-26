import { useAuthStore } from '@/store/authStore'

/**
 * Adiciona token JWT à URL de vídeo para autenticação no Nginx
 */
export function getAuthenticatedVideoUrl(videoPath: string): string {
  const token = useAuthStore.getState().accessToken
  
  if (!token) {
    console.warn('[Auth] Sem token para vídeo:', videoPath)
    return videoPath
  }
  
  // Para vídeos, precisamos usar um método diferente pois <video> não suporta headers
  // Solução: passar token como query param e validar no backend
  const url = new URL(videoPath, window.location.origin)
  url.searchParams.set('token', token)
  
  return url.toString()
}

/**
 * Cria headers de autenticação para fetch/axios
 */
export function getAuthHeaders(): HeadersInit {
  const token = useAuthStore.getState().accessToken
  
  if (!token) {
    return {}
  }
  
  return {
    'Authorization': `Bearer ${token}`
  }
}
