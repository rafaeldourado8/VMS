// ======================================================
// GT-Vision VMS - TypeScript Types
// ======================================================

// Auth
export interface User {
  id: number;
  email: string;
  name: string;
  role: 'admin' | 'viewer';
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access: string;
  refresh: string;
  user: User;
}

// Camera
export interface Camera {
  id: number;
  name: string;
  location: string | null;
  status: 'online' | 'offline';
  stream_url: string;
  thumbnail_url: string | null;
  snapshot_url: string | null;
  latitude: number | null;
  longitude: number | null;
  detection_settings: Record<string, unknown>;
  created_at: string;
  stream_url_frontend: string;
  ai_websocket_url: string;
}

export interface CameraCreateRequest {
  name: string;
  stream_url: string;
  location?: string;
  latitude?: number;
  longitude?: number;
}

// Detection
export interface Detection {
  id: number;
  camera_id: number;
  camera_name: string;
  plate: string | null;
  confidence: number | null;
  timestamp: string;
  vehicle_type: 'car' | 'motorcycle' | 'truck' | 'bus' | 'unknown';
  image_url: string | null;
  video_url: string | null;
}

// Dashboard
export interface DashboardStats {
  total_cameras: number;
  cameras_status: {
    online: number;
    offline: number;
  };
  detections_24h: number;
  detections_by_type: Record<string, number>;
  recent_activity: RecentActivity[];
  cached: boolean;
}

export interface RecentActivity {
  id: number;
  camera: string;
  plate: string | null;
  time: string;
  type: string;
}

// Streaming
export interface StreamInfo {
  path: string;
  source: string | null;
  ready: boolean;
  readers: number;
  bytes_received: number;
  bytes_sent: number;
}

export interface StreamStats {
  active_streams: number;
  total_viewers: number;
  total_bytes_sent: number;
  uptime_seconds: number;
  streams: StreamInfo[];
}

// API Response
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// WebSocket Events
export interface WSEvent {
  type: 'status' | 'detection' | 'alert' | 'ping' | 'pong';
  data?: unknown;
  timestamp: string;
}
