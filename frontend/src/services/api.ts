import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '@/store/authStore'
import type {
  AuthResponse,
  Camera,
  CameraCreateRequest,
  Clip,
  ClipCreateRequest,
  DashboardStats,
  Detection,
  LoginRequest,
  Mosaico,
  MosaicoCreateRequest,
  PaginatedResponse,
  User,
} from '@/types'

// Criar instância do Axios
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor para refresh token
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const refreshToken = useAuthStore.getState().refreshToken
      if (refreshToken) {
        try {
          const { data } = await axios.post<{ access: string }>('/api/auth/refresh/', {
            refresh: refreshToken,
          })
          
          useAuthStore.getState().updateTokens(data.access)
          originalRequest.headers.Authorization = `Bearer ${data.access}`
          
          return api(originalRequest)
        } catch {
          useAuthStore.getState().logout()
          window.location.href = '/login'
        }
      }
    }
    
    return Promise.reject(error)
  }
)

// ======================================================
// AUTH
// ======================================================

export const authService = {
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/login/', credentials)
    return data
  },

  async logout(refreshToken: string): Promise<void> {
    await api.post('/auth/logout/', { refresh_token: refreshToken })
  },

  async getMe(): Promise<User> {
    const { data } = await api.get<User>('/auth/me/')
    return data
  },
}

// ======================================================
// CAMERAS
// ======================================================

export const cameraService = {
  async list(): Promise<Camera[]> {
    const { data } = await api.get<Camera[] | PaginatedResponse<Camera>>('/cameras/')
    return Array.isArray(data) ? data : data.results
  },

  async get(id: number): Promise<Camera> {
    const { data } = await api.get<Camera>(`/cameras/${id}/`)
    return data
  },

  async create(camera: CameraCreateRequest): Promise<Camera> {
    const { data } = await api.post<Camera>('/cameras/', camera)
    return data
  },

  async update(id: number, camera: Partial<CameraCreateRequest>): Promise<Camera> {
    const { data } = await api.patch<Camera>(`/cameras/${id}/`, camera)
    return data
  },

  async delete(id: number): Promise<number> {
    const { data } = await api.delete<{ deleted_camera_id: number }>(`/cameras/${id}/`)
    // Limpar cache do frontend
    const { clearSnapshotByCamera } = await import('@/lib/snapshotCache')
    await clearSnapshotByCamera(id)
    return data.deleted_camera_id
  },

  async updateDetectionConfig(id: number, config: {
    roi_areas: any[]
    virtual_lines: any[]
    tripwires: any[]
    zone_triggers: any[]
    recording_retention_days?: number
    ai_enabled?: boolean
  }): Promise<void> {
    await api.post(`/cameras/${id}/update_detection_config/`, config)
  },

  async toggleAI(id: number, enabled: boolean): Promise<void> {
    await api.post(`/cameras/${id}/toggle_ai/`, { enabled })
  },
}

// ======================================================
// DETECTIONS
// ======================================================

export const detectionService = {
  async list(params?: {
    camera_id?: number
    plate?: string
    page?: number
  }): Promise<PaginatedResponse<Detection>> {
    const { data } = await api.get<PaginatedResponse<Detection>>('/deteccoes/list/', { params })
    return data
  },

  async get(id: number): Promise<Detection> {
    const { data } = await api.get<Detection>(`/deteccoes/${id}/`)
    return data
  },
}

// ======================================================
// DASHBOARD
// ======================================================

export const dashboardService = {
  async getStats(): Promise<DashboardStats> {
    const { data } = await api.get<DashboardStats>('/dashboard/stats/')
    return data
  },
}

// ======================================================
// STREAMING (via Streaming Service)
// ======================================================

export const streamingService = {
  async getStats() {
    const { data } = await axios.get('/streaming/stats')
    return data
  },

  async provisionCamera(cameraId: number, rtspUrl: string, name: string) {
    const { data } = await axios.post('/streaming/cameras/provision', {
      camera_id: cameraId,
      rtsp_url: rtspUrl,
      name,
      on_demand: true,
    })
    return data
  },

  async getCameraStatus(cameraId: number) {
    const { data } = await axios.get(`/streaming/cameras/${cameraId}/status`)
    return data
  },

  getHlsUrl(cameraId: number): string {
    return `/hls/cam_${cameraId}/index.m3u8`
  },
}

// ======================================================
// AI SERVICE
// ======================================================

export const aiService = {
  async getStatus(cameraId: number) {
    const { data } = await api.get(`/ai/cameras/${cameraId}/status/`)
    return data
  },

  async startProcessing(cameraId: number) {
    const { data } = await api.post(`/ai/cameras/${cameraId}/start/`)
    return data
  },

  async stopProcessing(cameraId: number) {
    const { data } = await api.post(`/ai/cameras/${cameraId}/stop/`)
    return data
  },

  async testDetection(cameraId: number) {
    const { data } = await api.post(`/ai/cameras/${cameraId}/test/`)
    return data
  },
}

// ======================================================
// RECORDINGS (via Storage Service)
// ======================================================

export const recordingService = {
  async list(params: {
    camera_id: number
    date: string
    start_time?: string
    end_time?: string
  }) {
    const storageUrl = import.meta.env.VITE_STORAGE_URL || '/storage'
    const { data } = await axios.get(`${storageUrl}/timeline/${params.camera_id}`, {
      params: { date: params.date, limit: 100 }
    })
    
    const recordings = (data.blocks || []).map((block: any) => {
      const startTime = new Date(block.start_time)
      const filename = `${startTime.getHours().toString().padStart(2, '0')}-${startTime.getMinutes().toString().padStart(2, '0')}-${startTime.getSeconds().toString().padStart(2, '0')}.mp4`
      
      return {
        camera_id: params.camera_id,
        date: params.date,
        file_name: filename,
        start_time: startTime.toTimeString().split(' ')[0],
        duration_seconds: block.duration_seconds,
        file_size_bytes: block.file_size_bytes,
        size_mb: (block.file_size_bytes / 1024 / 1024).toFixed(2)
      }
    })
    
    return {
      recordings,
      total_size_mb: recordings.reduce((sum: number, r: any) => sum + parseFloat(r.size_mb), 0).toFixed(2)
    }
  }
}

// ======================================================
// TIMELINE (via Storage Service)
// ======================================================

export const timelineService = {
  async getTimeline(cameraId: number, date?: string) {
    const storageUrl = import.meta.env.VITE_STORAGE_URL || '/storage'
    const params = date ? { date } : {}
    const { data } = await axios.get(`${storageUrl}/timeline/${cameraId}`, { params })
    return data
  }
}

export default api

// ======================================================
// CLIPS
// ======================================================

export const clipService = {
  async list(): Promise<Clip[]> {
    const { data } = await api.get<Clip[] | PaginatedResponse<Clip>>('/clips/clips/')
    return Array.isArray(data) ? data : data.results
  },

  async create(clip: ClipCreateRequest): Promise<Clip> {
    const { data } = await api.post<Clip>('/clips/clips/', clip)
    return data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/clips/clips/${id}/`)
  },

  async getStatus(id: number): Promise<{ status: string }> {
    const { data } = await api.get(`/clips/clips/${id}/status/`)
    return data
  },
}

// ======================================================
// MOSAICOS
// ======================================================

export const mosaicoService = {
  async list(): Promise<Mosaico[]> {
    const { data } = await api.get<Mosaico[] | PaginatedResponse<Mosaico>>('/mosaicos/')
    return Array.isArray(data) ? data : data.results
  },

  async create(mosaico: MosaicoCreateRequest): Promise<Mosaico> {
    const { data } = await api.post<Mosaico>('/mosaicos/', mosaico)
    return data
  },

  async updateCameras(id: number, cameras: { camera_id: number; position: number }[]): Promise<Mosaico> {
    const { data } = await api.post<Mosaico>(`/mosaicos/${id}/update_cameras/`, { cameras })
    return data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/mosaicos/${id}/`)
  },
}
