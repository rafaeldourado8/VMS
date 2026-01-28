# 🏗️ DVR-Lite - Arquitetura

Arquitetura simplificada focada em streaming e gravação.

---

## 📐 Diagrama

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  - Live Streaming (HLS)                                  │
│  - Playback Player                                       │
│  - Timeline Component                                    │
│  - Clip Management                                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼────────────────────────────────────┐
│              Backend API (Django)                        │
│  - Auth & Users                                          │
│  - Camera Management                                     │
│  - Recording API                                         │
│  - Playback API                                          │
│  - Clip API                                              │
└─┬──────────┬──────────┬──────────┬────────────┬─────────┘
  │          │          │          │            │
  ▼          ▼          ▼          ▼            ▼
┌───────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│Postgre│ │Redis │ │RabbitMQ│ │MediaMTX│ │Recording │
│  SQL  │ │Cache │ │ Queue  │ │Streaming│ │ Service  │
└───────┘ └──────┘ └────────┘ └───┬────┘ └────┬─────┘
                                   │           │
                              ┌────▼───────────▼─────┐
                              │   S3 Storage         │
                              │  - recordings/       │
                              │  - clips/            │
                              └──────────────────────┘
                                   ▲
                              ┌────┴─────┐
                              │ Cameras  │
                              │ RTSP/RTMP│
                              └──────────┘
```

---

## 🔄 Fluxos Principais

### 1. Live Streaming
```
Camera → MediaMTX → HLS → Frontend
```

### 2. Recording
```
MediaMTX → Recording Service → S3
         ↓
    PostgreSQL (metadata)
```

### 3. Playback
```
Frontend → Backend API → S3 → Frontend
                       ↓
                   PostgreSQL (query)
```

### 4. Clip Creation
```
Frontend → Backend API → Celery Task → FFmpeg → S3
                                              ↓
                                         PostgreSQL
```

---

## 🗄️ Database Schema

### Users
```sql
- id
- email
- password_hash
- parent_user_id (FK)
- created_at
```

### Cameras
```sql
- id
- name
- rtsp_url
- user_id (FK)
- is_active
- created_at
```

### Recordings
```sql
- id
- camera_id (FK)
- start_time
- end_time
- file_path (S3)
- size_bytes
- is_permanent
- created_at
```

### Clips
```sql
- id
- recording_id (FK)
- user_id (FK)
- name
- start_time
- end_time
- duration
- file_path (S3)
- created_at
```

### UserPermissions
```sql
- id
- user_id (FK)
- camera_id (FK)
- can_view
- can_playback
- can_clip
```

---

## 🔌 APIs Principais

### Auth
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me

### Cameras
- GET /api/cameras/
- POST /api/cameras/
- PUT /api/cameras/{id}/
- DELETE /api/cameras/{id}/

### Recordings
- GET /api/recordings/
- GET /api/recordings/{camera_id}/
- GET /api/recordings/{camera_id}/date/{date}/

### Playback
- GET /api/playback/stream/{recording_id}/

### Clips
- GET /api/clips/
- POST /api/clips/
- GET /api/clips/{id}/
- DELETE /api/clips/{id}/
- GET /api/clips/{id}/download/

### Users
- GET /api/users/sub-users/
- POST /api/users/sub-users/
- PUT /api/users/sub-users/{id}/
- DELETE /api/users/sub-users/{id}/

---

## 📦 Componentes

### Frontend
- React 18
- TypeScript
- TailwindCSS
- video.js / plyr.io
- date-fns

### Backend
- Django 4.2
- Django REST Framework
- Celery
- boto3 (S3)
- FFmpeg

### Infrastructure
- PostgreSQL 15
- Redis 7
- RabbitMQ 3.13
- MediaMTX

---

## 🔐 Segurança

- JWT authentication
- HTTPS obrigatório
- CORS configurado
- Rate limiting
- Input validation
- S3 presigned URLs
- IAM roles (AWS)

---

## 📊 Monitoring

- CloudWatch Logs
- CloudWatch Metrics
- Health checks
- Error tracking
- Performance metrics
