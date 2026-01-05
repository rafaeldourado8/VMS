// Use Case: Draw ROI
import { Polygon } from '../../domain/value-objects/Polygon';
import { Point } from '../../domain/value-objects/Point';
import { ApiClient } from '../../infrastructure/api/ApiClient';

export class DrawROIUseCase {
  constructor(private apiClient: ApiClient) {}

  async execute(cameraId: number, points: Point[]): Promise<void> {
    if (cameraId <= 0) {
      throw new Error('ID da câmera inválido');
    }

    if (points.length < 3) {
      throw new Error('ROI deve ter no mínimo 3 pontos');
    }

    // Cria polígono para validar
    const polygon = new Polygon(points);

    // Envia para API
    await this.apiClient.updateROI(cameraId, polygon.toArray());
  }
}
