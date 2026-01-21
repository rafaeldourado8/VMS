// Infrastructure: API Client
import axios, { AxiosInstance } from 'axios';
import { Camera } from '../../domain/entities/Camera';
import { Detection } from '../../domain/entities/Detection';

export class ApiClient {
  public client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:8000/api') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // Interceptor para adicionar token em todas as requisições
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  // Cameras
  async getCameras(): Promise<Camera[]> {
    const response = await this.client.get('/cameras/');
    return response.data;
  }

  async createCamera(data: Partial<Camera>): Promise<Camera> {
    const response = await this.client.post('/cameras/', data);
    return response.data;
  }

  async deleteCamera(id: number): Promise<void> {
    await this.client.delete(`/cameras/${id}/`);
  }

  // Detections
  async getDetections(cameraId?: number, plate?: string): Promise<Detection[]> {
    const params: any = {};
    if (cameraId) params.camera_id = cameraId;
    if (plate) params.plate = plate;
    
    const response = await this.client.get('/detections/', { params });
    return response.data;
  }

  // AI
  async toggleAI(cameraId: number, enabled: boolean): Promise<void> {
    await this.client.post(`http://localhost:8002/ai/toggle/${cameraId}`, { enabled });
  }

  async getAIStatus(cameraId: number): Promise<{ ai_enabled: boolean }> {
    const response = await this.client.get(`http://localhost:8002/ai/status/${cameraId}`);
    return response.data;
  }
}

export const apiClient = new ApiClient();
