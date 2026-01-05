// Infrastructure: API Client
import axios, { AxiosInstance } from 'axios';
import { Camera } from '../../domain/entities/Camera';
import { Detection } from '../../domain/entities/Detection';

export class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:8000/api') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
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

  async updateROI(cameraId: number, points: [number, number][]): Promise<void> {
    await this.client.post(`http://localhost:8002/ai/roi/${cameraId}`, {
      polygon_points: points,
      enabled: true,
    });
  }

  async getAIStatus(cameraId: number): Promise<{ ai_enabled: boolean; has_roi: boolean }> {
    const response = await this.client.get(`http://localhost:8002/ai/status/${cameraId}`);
    return response.data;
  }
}

export const apiClient = new ApiClient();
