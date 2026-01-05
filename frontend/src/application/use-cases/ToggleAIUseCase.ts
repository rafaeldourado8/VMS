// Use Case: Toggle AI
import { ApiClient } from '../../infrastructure/api/ApiClient';

export class ToggleAIUseCase {
  constructor(private apiClient: ApiClient) {}

  async execute(cameraId: number, enabled: boolean): Promise<void> {
    if (cameraId <= 0) {
      throw new Error('ID da câmera inválido');
    }

    await this.apiClient.toggleAI(cameraId, enabled);
  }
}
