// Domain Entity: Camera
export interface Camera {
  id: number;
  name: string;
  location?: string;
  status: 'online' | 'offline';
  streamUrl: string;
  hlsUrl?: string;
  thumbnailUrl?: string;
  latitude?: number;
  longitude?: number;
  recordingEnabled: boolean;
  aiEnabled?: boolean;
  hasROI?: boolean;
}

export class CameraEntity implements Camera {
  constructor(
    public id: number,
    public name: string,
    public streamUrl: string,
    public status: 'online' | 'offline' = 'online',
    public location?: string,
    public hlsUrl?: string,
    public thumbnailUrl?: string,
    public latitude?: number,
    public longitude?: number,
    public recordingEnabled: boolean = true,
    public aiEnabled: boolean = true,
    public hasROI: boolean = false
  ) {}

  isOnline(): boolean {
    return this.status === 'online';
  }

  hasAI(): boolean {
    return this.aiEnabled === true;
  }

  hasLocation(): boolean {
    return this.latitude !== undefined && this.longitude !== undefined;
  }
}
