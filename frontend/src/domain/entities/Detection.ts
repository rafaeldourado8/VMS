// Domain Entity: Detection
export interface Detection {
  id: number;
  cameraId: number;
  plate?: string;
  confidence?: number;
  timestamp: Date;
  vehicleType: 'car' | 'motorcycle' | 'truck' | 'bus' | 'unknown';
  imageUrl?: string;
  videoUrl?: string;
}

export class DetectionEntity implements Detection {
  constructor(
    public id: number,
    public cameraId: number,
    public timestamp: Date,
    public vehicleType: 'car' | 'motorcycle' | 'truck' | 'bus' | 'unknown' = 'unknown',
    public plate?: string,
    public confidence?: number,
    public imageUrl?: string,
    public videoUrl?: string
  ) {}

  hasPlate(): boolean {
    return this.plate !== undefined && this.plate.length > 0;
  }

  isHighConfidence(): boolean {
    return this.confidence !== undefined && this.confidence >= 0.8;
  }

  hasEvidence(): boolean {
    return this.imageUrl !== undefined || this.videoUrl !== undefined;
  }
}
