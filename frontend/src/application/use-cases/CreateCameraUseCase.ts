// Use Case: Create Camera
import { Camera } from '../../domain/entities/Camera';
import { ApiClient } from '../../infrastructure/api/ApiClient';

export interface CreateCameraDTO {
  name: string;
  streamUrl: string;
  location?: string;
  latitude?: number;
  longitude?: number;
}

export class CreateCameraUseCase {
  constructor(private apiClient: ApiClient) {}

  async execute(data: CreateCameraDTO): Promise<Camera> {
    // Validações
    if (!data.name || data.name.trim().length === 0) {
      throw new Error('Nome da câmera é obrigatório');
    }

    if (!data.streamUrl || !data.streamUrl.startsWith('rtsp://')) {
      throw new Error('URL RTSP inválida');
    }

    // Executa criação
    return await this.apiClient.createCamera(data);
  }
}
