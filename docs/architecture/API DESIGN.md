# VMS — API Design Documentation

## API Architecture Overview

```mermaid
graph TB
    subgraph "Client"
        Frontend[React Frontend]
    end

    subgraph "Entry Point"
        HAProxy[HAProxy :80]
    end

    subgraph "API Gateway"
        Kong[Kong Gateway]
    end

    subgraph "Backend APIs"
        Django[Django REST API :8000]
        Streaming[Streaming API :8001]
        AI[AI Detection API :8002]
    end

    Frontend -->|HTTP/HTTPS| HAProxy
    HAProxy -->|/api/*| Kong
    HAProxy -->|/api/streaming/*| Streaming
    HAProxy -->|/api/ai/*| AI
    Kong -->|Route| Django
    
    style Frontend fill:#e1f5ff
    style HAProxy fill:#fff4e6
    style Kong fill:#fff4e6
    style Django fill:#e8f5e9
    style Streaming fill:#e8f5e9
    style AI fill:#e8f5e9
```

## Base URLs

| Service | Base URL | Description |
|---------|----------|-------------|
| Django Backend | `http://localhost/api` | Main business logic |
| Streaming Service | `http://localhost/api/streaming` | Stream management |
| AI Detection | `http://localhost/api/ai` | AI operations |
| MediaMTX HLS | `http://localhost/hls` | Video streaming |
| Admin Panel | `http://localhost/admin` | Django admin |

## Authentication

### JWT Token Authentication

All API requests (except login) require JWT token in header:

```http
Authorization: Bearer <access_token>
```

### Token Endpoints

#### 1. Login (Obtain Token)
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**Response 200:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User"
  }
}
```

#### 2. Refresh Token
```http
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response 200:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### 3. Logout
```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response 200:**
```json
{
  "message": "Logout successful"
}
```

#### 4. Get Current User
```http
GET /api/auth/me/
Authorization: Bearer <access_token>
```

**Response 200:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "is_staff": true,
  "is_superuser": true
}
```

---

## Django Backend API

### Cameras API

#### 1. List Cameras
```http
GET /api/cameras/
Authorization: Bearer <token>
```

**Response 200:**
```json
[
  {
    "id": 1,
    "name": "Entrance Camera",
    "location": "Main Gate",
    "status": "online",
    "stream_url": "rtsp://admin:pass@192.168.1.100:554/stream1",
    "thumbnail_url": "/media/thumbnails/cam_1.jpg",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "ai_enabled": true,
    "recording_enabled": true,
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": "2026-01-08T10:00:00Z"
  }
]
```

#### 2. Get Camera Details
```http
GET /api/cameras/{id}/
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "id": 1,
  "name": "Entrance Camera",
  "location": "Main Gate",
  "status": "online",
  "stream_url": "rtsp://admin:pass@192.168.1.100:554/stream1",
  "thumbnail_url": "/media/thumbnails/cam_1.jpg",
  "latitude": -23.5505,
  "longitude": -46.6333,
  "ai_enabled": true,
  "recording_enabled": true,
  "roi_areas": [
    {
      "name": "Gate Area",
      "points": [
        {"x": 100, "y": 100},
        {"x": 500, "y": 100},
        {"x": 500, "y": 400},
        {"x": 100, "y": 400}
      ]
    }
  ],
  "created_at": "2026-01-08T10:00:00Z",
  "updated_at": "2026-01-08T10:00:00Z"
}
```

#### 3. Create Camera
```http
POST /api/cameras/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Parking Camera",
  "location": "Parking Lot",
  "stream_url": "rtsp://admin:pass@192.168.1.101:554/stream1",
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

**Response 201:**
```json
{
  "id": 2,
  "name": "Parking Camera",
  "location": "Parking Lot",
  "status": "online",
  "stream_url": "rtsp://admin:pass@192.168.1.101:554/stream1",
  "latitude": -23.5505,
  "longitude": -46.6333,
  "ai_enabled": false,
  "recording_enabled": true,
  "created_at": "2026-01-08T11:00:00Z"
}
```

#### 4. Update Camera
```http
PATCH /api/cameras/{id}/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Camera Name",
  "location": "New Location"
}
```

**Response 200:**
```json
{
  "id": 2,
  "name": "Updated Camera Name",
  "location": "New Location",
  "status": "online",
  "updated_at": "2026-01-08T12:00:00Z"
}
```

#### 5. Delete Camera
```http
DELETE /api/cameras/{id}/
Authorization: Bearer <token>
```

**Response 204:** No Content

#### 6. Toggle AI
```http
POST /api/cameras/{id}/toggle_ai/
Authorization: Bearer <token>
Content-Type: application/json

{
  "enabled": true
}
```

**Response 200:**
```json
{
  "success": true,
  "ai_enabled": true,
  "camera_id": 2
}
```

#### 7. Update Detection Config
```http
POST /api/cameras/{id}/update_detection_config/
Authorization: Bearer <token>
Content-Type: application/json

{
  "roi_areas": [
    {
      "name": "Detection Zone",
      "points": [
        {"x": 100, "y": 100},
        {"x": 500, "y": 100},
        {"x": 500, "y": 400},
        {"x": 100, "y": 400}
      ]
    }
  ],
  "recording_retention_days": 30
}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Configurações atualizadas"
}
```

#### 8. Get Stream Status
```http
GET /api/cameras/{id}/stream_status/
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "camera_id": 2,
  "status": "active",
  "viewers": 3,
  "hls_url": "/hls/cam_2/index.m3u8",
  "mediamtx_ready": true
}
```

#### 9. Reprovision All Cameras
```http
POST /api/cameras/reprovision/
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "success": 5,
  "failed": 0,
  "total": 5,
  "message": "5/5 câmeras reprovisionadas"
}
```

### Detections API

#### 1. List Detections
```http
GET /api/detections/?camera_id=2&page=1
Authorization: Bearer <token>
```

**Query Parameters:**
- `camera_id` (optional): Filter by camera
- `plate` (optional): Filter by license plate
- `page` (optional): Page number
- `page_size` (optional): Items per page (default: 20)

**Response 200:**
```json
{
  "count": 150,
  "next": "/api/detections/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "camera_id": 2,
      "timestamp": "2026-01-08T10:30:45Z",
      "class_name": "license_plate",
      "confidence": 0.87,
      "bbox": [120, 200, 280, 250],
      "plate_text": "ABC1234",
      "plate_confidence": 0.92,
      "vehicle_type": "car",
      "frame_url": "/media/detections/cam_2_20260108_103045.jpg"
    }
  ]
}
```

#### 2. Get Detection Details
```http
GET /api/detections/{id}/
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "id": 1,
  "camera": {
    "id": 2,
    "name": "Parking Camera"
  },
  "timestamp": "2026-01-08T10:30:45Z",
  "class_name": "license_plate",
  "confidence": 0.87,
  "bbox": [120, 200, 280, 250],
  "plate_text": "ABC1234",
  "plate_confidence": 0.92,
  "vehicle_type": "car",
  "vehicle_color": "blue",
  "frame_url": "/media/detections/cam_2_20260108_103045.jpg",
  "processed": true
}
```

### Dashboard API

#### 1. Get Dashboard Stats
```http
GET /api/dashboard/stats/
Authorization: Bearer <token>
```

**Response 200:**
```json
{
  "total_cameras": 5,
  "active_cameras": 4,
  "total_detections": 150,
  "period": "24h"
}
```

### Clips API

#### 1. List Clips
```http
GET /api/clips/
Authorization: Bearer <token>
```

**Response 200:**
```json
[
  {
    "id": 1,
    "camera_id": 2,
    "name": "Incident at Gate",
    "start_time": "2026-01-08T10:00:00Z",
    "end_time": "2026-01-08T10:05:00Z",
    "duration": 300,
    "file_url": "/media/clips/clip_1.mp4",
    "created_at": "2026-01-08T10:10:00Z"
  }
]
```

#### 2. Create Clip
```http
POST /api/clips/
Authorization: Bearer <token>
Content-Type: application/json

{
  "camera_id": 2,
  "name": "Security Event",
  "start_time": "2026-01-08T10:00:00Z",
  "end_time": "2026-01-08T10:05:00Z"
}
```

**Response 201:**
```json
{
  "id": 2,
  "camera_id": 2,
  "name": "Security Event",
  "start_time": "2026-01-08T10:00:00Z",
  "end_time": "2026-01-08T10:05:00Z",
  "status": "processing"
}
```

---

## Streaming Service API

Base URL: `/api/streaming` or direct `http://streaming:8001`

### 1. Health Check
```http
GET /api/streaming/health
```

**Response 200:**
```json
{
  "status": "ok"
}
```

### 2. Provision Stream
```http
POST /api/streaming/cameras/provision
Content-Type: application/json

{
  "camera_id": 2,
  "rtsp_url": "rtsp://admin:pass@192.168.1.100:554/stream1",
  "name": "Parking Camera",
  "on_demand": true
}
```

**Response 200:**
```json
{
  "success": true,
  "camera_id": 2,
  "stream_path": "cam_2",
  "hls_url": "/hls/cam_2/index.m3u8",
  "message": "Stream provisionado com sucesso"
}
```

**Response 409 (Already Exists):**
```json
{
  "detail": "Stream already exists for camera 2"
}
```

### 3. Remove Stream
```http
DELETE /api/streaming/cameras/{camera_id}
```

**Response 200:**
```json
{
  "success": true,
  "message": "Stream removido"
}
```

### 4. Get Stream Status
```http
GET /api/streaming/cameras/{camera_id}/status
```

**Response 200:**
```json
{
  "camera_id": 2,
  "status": "active",
  "viewers": 3,
  "hls_url": "/hls/cam_2/index.m3u8",
  "mediamtx_ready": true
}
```

### 5. List All Streams
```http
GET /api/streaming/streams
```

**Response 200:**
```json
[
  {
    "camera_id": 1,
    "path": "cam_1",
    "status": "active",
    "viewers": 2,
    "hls_url": "/hls/cam_1/index.m3u8"
  },
  {
    "camera_id": 2,
    "path": "cam_2",
    "status": "idle",
    "viewers": 0,
    "hls_url": "/hls/cam_2/index.m3u8"
  }
]
```

---

## AI Detection Service API

Base URL: `/api/ai` or direct `http://ai_detection:8002`

### 1. Health Check
```http
GET /api/ai/health
```

**Response 200:**
```json
{
  "status": "ok",
  "service": "ai_detection"
}
```

### 2. Start AI Detection
```http
POST /api/ai/cameras/{camera_id}/start/
```

**Response 200:**
```json
{
  "success": true,
  "camera_id": 2,
  "ai_enabled": true
}
```

### 3. Stop AI Detection
```http
POST /api/ai/cameras/{camera_id}/stop/
```

**Response 200:**
```json
{
  "success": true,
  "camera_id": 2,
  "ai_enabled": false
}
```

### 4. Get AI Status
```http
GET /api/ai/cameras/{camera_id}/status/
```

**Response 200:**
```json
{
  "camera_id": 2,
  "ai_enabled": true,
  "has_roi": true
}
```

### 5. Test Detection
```http
POST /api/ai/cameras/{camera_id}/test/
```

**Response 200:**
```json
{
  "success": true,
  "message": "Teste de detecção executado com sucesso",
  "camera_id": 2,
  "has_roi": true
}
```

### 6. Update ROI
```http
POST /api/ai/roi/{camera_id}
Content-Type: application/json

{
  "polygon_points": [
    [100, 100],
    [500, 100],
    [500, 400],
    [100, 400]
  ],
  "enabled": true,
  "name": "Detection Zone"
}
```

**Response 200:**
```json
{
  "success": true,
  "camera_id": 2,
  "roi_name": "Detection Zone",
  "enabled": true,
  "points_count": 4
}
```

### 7. List Cameras with AI
```http
GET /api/ai/cameras
```

**Response 200:**
```json
{
  "cameras": [
    {
      "camera_id": 1,
      "ai_enabled": true
    },
    {
      "camera_id": 2,
      "ai_enabled": false
    }
  ]
}
```

---

## Error Responses

### Standard Error Format

All APIs return errors in this format:

```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | No permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Example Error Responses

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**404 Not Found:**
```json
{
  "detail": "Camera with id 999 not found."
}
```

**400 Bad Request:**
```json
{
  "name": ["This field is required."],
  "stream_url": ["Enter a valid URL."]
}
```

---

## Rate Limiting

Configured via Kong Gateway:

| Endpoint Pattern | Limit | Window |
|-----------------|-------|--------|
| `/api/*` | 100 requests | per minute |
| `/api/streaming/*` | 500 requests | per minute |
| `/api/ai/*` | 100 requests | per minute |

**Rate Limit Headers:**
```http
X-RateLimit-Limit-Minute: 100
X-RateLimit-Remaining-Minute: 95
```

**Rate Limit Exceeded (429):**
```json
{
  "message": "API rate limit exceeded"
}
```

---

## CORS Configuration

**Allowed Origins:**
- `http://localhost:5173` (Vite dev server)
- `http://localhost` (Production)

**Allowed Methods:**
- GET, POST, PUT, PATCH, DELETE, OPTIONS

**Allowed Headers:**
- Authorization, Content-Type, Accept

---

## Pagination

List endpoints support pagination:

**Request:**
```http
GET /api/cameras/?page=2&page_size=10
```

**Response:**
```json
{
  "count": 50,
  "next": "/api/cameras/?page=3&page_size=10",
  "previous": "/api/cameras/?page=1&page_size=10",
  "results": [...]
}
```

**Default page_size:** 20  
**Max page_size:** 100

---

## WebSocket Events (Future)

Real-time notifications via WebSocket:

```javascript
const ws = new WebSocket('ws://localhost/ws/events/');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data);
};
```

**Event Types:**
- `detection.created`: New detection
- `camera.status_changed`: Camera online/offline
- `stream.started`: Stream began
- `stream.stopped`: Stream ended

---

## API Versioning

Current version: **v1** (implicit)

Future versions will use URL prefix:
- `/api/v1/cameras/`
- `/api/v2/cameras/`

---

## SDK / Client Libraries

### JavaScript/TypeScript (Frontend)

```typescript
// services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Camera service
export const cameraService = {
  list: () => api.get('/cameras/'),
  get: (id) => api.get(`/cameras/${id}/`),
  create: (data) => api.post('/cameras/', data),
  update: (id, data) => api.patch(`/cameras/${id}/`, data),
  delete: (id) => api.delete(`/cameras/${id}/`),
  toggleAI: (id, enabled) => 
    api.post(`/cameras/${id}/toggle_ai/`, { enabled }),
};
```

### Python (Backend Integration)

```python
import requests

class VMSClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def list_cameras(self):
        response = requests.get(
            f'{self.base_url}/api/cameras/',
            headers=self.headers
        )
        return response.json()
    
    def create_camera(self, data):
        response = requests.post(
            f'{self.base_url}/api/cameras/',
            json=data,
            headers=self.headers
        )
        return response.json()
```

---

## Testing

### Health Check All Services

```bash
# Backend
curl http://localhost/api/health/

# Streaming
curl http://localhost/api/streaming/health

# AI Detection
curl http://localhost/api/ai/health
```

### Authentication Flow

```bash
# 1. Login
TOKEN=$(curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access')

# 2. Use token
curl http://localhost/api/cameras/ \
  -H "Authorization: Bearer $TOKEN"
```

### Create Camera End-to-End

```bash
# 1. Create camera
curl -X POST http://localhost/api/cameras/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Camera",
    "location": "Test Location",
    "stream_url": "rtsp://admin:pass@192.168.1.100:554/stream1"
  }'

# 2. Verify stream provisioned
curl http://localhost/api/streaming/cameras/1/status

# 3. Access HLS stream
curl http://localhost/hls/cam_1/index.m3u8
```
